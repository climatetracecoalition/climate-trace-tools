import pandas as pd
import os
import zipfile
import requests
import networkx as nx
from tqdm import tqdm
import time
from pathlib import Path

# Climate TRACE API base URL
API_BASE_URL = "https://api.climatetrace.org/v6"

DEFAULT_OWNERSHIP_ZIP = Path(__file__).parent.parent / "data" / "ownership" / "ownership.zip"


def _load_csv_from_zip(zf, pattern_include, pattern_exclude=None):
    """Find and load a CSV from a zip file by partial name match."""
    matches = [
        n
        for n in zf.namelist()
        if pattern_include in n
        and n.endswith(".csv")
        and (pattern_exclude is None or pattern_exclude not in n)
    ]
    if not matches:
        raise FileNotFoundError(f"No CSV containing '{pattern_include}' found in zip")
    with zf.open(matches[0]) as f:
        return pd.read_csv(f)


def load_ownership_data(ownership_zip=None):
    """
    Load all three ownership DataFrames from the ownership zip file.

    Parameters:
        ownership_zip: path to ownership.zip

    Returns:
        tuple: (asset_to_owner_df, all_entities_df, all_entity_connections_df)
    """
    if ownership_zip is None:
        ownership_zip = DEFAULT_OWNERSHIP_ZIP
    with zipfile.ZipFile(ownership_zip, "r") as zf:
        asset_to_owner_df = _load_csv_from_zip(zf, "entity_asset_relationships")
        all_entities_df = _load_csv_from_zip(zf, "all_entities_", "relationships")
        all_entity_connections_df = _load_csv_from_zip(
            zf, "entity_relationships", "asset"
        )

    asset_to_owner_df = asset_to_owner_df[asset_to_owner_df["source_id"].notna()]
    asset_to_owner_df["source_id"] = (
        asset_to_owner_df["source_id"].astype(int).astype(str)
    )

    return asset_to_owner_df, all_entities_df, all_entity_connections_df


def build_ownership_graph(
    asset_to_owner_df, all_entities_df, all_entity_connections_df
):
    """
    Build a directed ownership graph from the three ownership DataFrames.

    Nodes are either entities (owners) or assets (Climate TRACE sources).
    Edges represent ownership relationships.

    Returns:
        nx.DiGraph with entities and assets as nodes, ownership as edges
    """
    G = nx.DiGraph()

    # Add entities as nodes
    for _, row in all_entities_df.iterrows():
        entity_id = row["Entity ID"]
        entity_name = row["Full Name"] if pd.notna(row["Full Name"]) else row["Name"]
        G.add_node(entity_id, type="entity", name=entity_name)

    # Add assets as nodes
    for _, row in asset_to_owner_df.iterrows():
        source_id = row["source_id"]
        if pd.notna(source_id):
            G.add_node(str(source_id), type="asset", name=row["source_name"])

    # Add entity-to-entity ownership edges
    for _, row in all_entity_connections_df.iterrows():
        owner_id = row["owner_entity_id"]
        subject_id = row["subject_entity_id"]
        if pd.notna(owner_id) and pd.notna(subject_id):
            if not G.has_node(owner_id):
                G.add_node(owner_id, type="entity", name="Unknown Entity")
            if not G.has_node(subject_id):
                G.add_node(subject_id, type="entity", name="Unknown Entity")
            G.add_edge(
                owner_id,
                subject_id,
                relation_type="owns_entity",
                percent_of_ownership=row.get("percent_of_ownership"),
            )

    # Add entity-to-asset ownership edges
    for _, row in asset_to_owner_df.iterrows():
        owner_id = row["immediate_source_owner_entity_id"]
        asset_id = str(row["source_id"]) if pd.notna(row["source_id"]) else None
        if pd.notna(owner_id) and asset_id:
            if not G.has_node(owner_id):
                G.add_node(owner_id, type="entity", name="Unknown Entity")
            if not G.has_node(asset_id):
                G.add_node(asset_id, type="asset", name="Unknown Asset")
            G.add_edge(owner_id, asset_id, relation_type="owns_asset")

    return G


# API functions
def get_asset_details(source_id):
    """Fetch asset details from Climate TRACE API."""
    url = f"{API_BASE_URL}/assets/{source_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def find_owner_sources(owner_name, ownership_file=None):
    """
    Find Climate TRACE source IDs associated with a given asset owner (immediate ownership only).

    Parameters:
        owner_name: name of the asset owner to look up
        ownership_file: path to the ownership CSV file, or path to ownership.zip

    Returns:
        list of unique source IDs associated with the owner
    """
    if ownership_file is None:
        ownership_file = DEFAULT_OWNERSHIP_ZIP
    if str(ownership_file).endswith(".zip"):
        with zipfile.ZipFile(ownership_file, "r") as zf:
            ownership_df = _load_csv_from_zip(zf, "entity_asset_relationships")
    else:
        ownership_df = pd.read_csv(ownership_file)

    ownership_df = ownership_df[ownership_df["source_id"].notna()]
    ownership_df["source_id"] = ownership_df["source_id"].astype(int)
    ownership_df["immediate_source_owner"] = ownership_df[
        "immediate_source_owner"
    ].str.strip()

    owner_df = ownership_df[ownership_df["immediate_source_owner"] == owner_name]
    if owner_df.empty:
        raise ValueError(f"Owner '{owner_name}' not found in ownership data")

    return list(owner_df["source_id"].unique())


def find_owners_emissions(sources, gas="co2e_100yr", year=2024):
    """Fetch emissions for a list of source IDs using the Climate TRACE API."""
    results = []

    for source_id in tqdm(sources):
        asset = get_asset_details(source_id)
        time.sleep(0.1)

        if asset is None:
            continue

        emissions_data = asset.get("EmissionsDetails", [])
        year_emissions = [
            e for e in emissions_data if e.get("Year") == year and e.get("Gas") == gas
        ]

        if year_emissions:
            emissions_quantity = sum(
                e.get("EmissionsQuantity", 0) for e in year_emissions
            )
        else:
            emissions_quantity = 0

        results.append(
            {
                "source_id": asset.get("Id"),
                "source_name": asset.get("Name"),
                "source_type": asset.get("AssetType"),
                "iso3_country": asset.get("Country"),
                "subsector": asset.get("Sector"),
                "year": year,
                "gas": gas,
                "emissions_quantity": emissions_quantity,
            }
        )

    return pd.DataFrame(results)


def get_assets_owned_by_entity(entity_name, ownership_zip=None, gas="co2e_100yr", year=2024):
    """
    Find all assets an entity has direct and indirect ownership in, with emissions data.

    Traverses the full ownership network (including indirect ownership chains) to find
    all assets associated with the entity. Emissions are not prorated by ownership percentage.

    Parameters:
        entity_name: Full name of the entity to look up (e.g., 'BlackRock Inc')
        ownership_zip: Path to ownership.zip
        gas: Gas of interest (default: 'co2e_100yr')
        year: Year of emissions data (default: 2024)

    Returns:
        DataFrame with columns: Owner Entity ID, Owner, source_id, source_name,
        source_sector, source_subsector, and emissions data for the specified year and gas.
    """
    asset_to_owner_df, all_entities_df, all_entity_connections_df = load_ownership_data(
        ownership_zip
    )
    G = build_ownership_graph(
        asset_to_owner_df, all_entities_df, all_entity_connections_df
    )

    entities_dic = all_entities_df.set_index("Full Name")["Entity ID"].to_dict()
    entity_id = entities_dic.get(entity_name)
    if entity_id is None:
        raise ValueError(f"Entity '{entity_name}' not found in ownership data")

    source_ids = list(asset_to_owner_df["source_id"].unique())
    subgraph_nodes = list(nx.descendants(G, entity_id))
    subgraph_source_ids = [x for x in subgraph_nodes if x in source_ids]

    sources = []
    for source in tqdm(subgraph_source_ids):
        paths = nx.all_simple_paths(G, source=entity_id, target=source)
        if len(list(paths)) >= 1:
            sources.append(source)

    df = pd.DataFrame(
        {
            "Owner Entity ID": entity_id,
            "Owner": entity_name,
            "source_id": sources,
        }
    )

    df = df.merge(
        asset_to_owner_df[
            ["source_id", "source_name", "source_sector", "source_subsector"]
        ],
        on="source_id",
        how="left",
    )
    df = df.drop_duplicates(subset=["source_id"])

    print("Calculating Emissions")
    owner_sources = list(df["source_id"].unique())
    owners_emissions = find_owners_emissions(owner_sources, gas=gas, year=year)
    owners_emissions["source_id"] = (
        owners_emissions["source_id"].astype(int).astype(str)
    )

    df = df.merge(owners_emissions, how="left", on="source_id")
    df = df.drop_duplicates(subset=["source_id"])

    return df
