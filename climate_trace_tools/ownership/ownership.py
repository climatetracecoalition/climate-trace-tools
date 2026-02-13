import pandas as pd
import os
import zipfile
import io
import requests

# Climate TRACE API base URL
API_BASE_URL = 'https://api.climatetrace.org/v6'

# API functions
def get_asset_details(source_id):
    """Fetch asset details from Climate TRACE API."""
    url = f"{API_BASE_URL}/assets/{source_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def find_owner_sources(owner_name, ownership_file):
    """
    Find Climate TRACE source IDs associated with a given asset owner.

    Parameters:
        owner_name: name of the asset owner to look up
        ownership_file: path to the ownership CSV file, or path to the ownership.zip
                        (will read ownership_all_entity_asset_relationships_December_2025.csv from within it)

    Returns:
        list of unique source IDs associated with the owner
    """
    if ownership_file.endswith('.zip'):
        with zipfile.ZipFile(ownership_file, 'r') as zf:
            csv_name = 'ownership_all_entity_asset_relationships_December_2025.csv'
            with zf.open(csv_name) as f:
                ownership_df = pd.read_csv(f)
    else:
        ownership_df = pd.read_csv(ownership_file)
    ownership_df = ownership_df[ownership_df['source_id'].notna()]
    ownership_df['source_id'] = ownership_df['source_id'].astype(int)
    ownership_df['immediate_source_owner'] = ownership_df['immediate_source_owner'].str.strip()

    owner_df = ownership_df[ownership_df['immediate_source_owner'] == owner_name]
    if owner_df.empty:
        raise ValueError(f"Owner '{owner_name}' not found in {ownership_file}")

    return list(owner_df['source_id'].unique())

def find_owners_emissions(sources, gas='co2e_100yr', year=2024):
    """Fetch emissions for a list of source IDs using the Climate TRACE API."""
    results = []

    for source_id in sources:
        asset = get_asset_details(source_id)
        if asset is None:
            continue

        # Extract emissions for the specified year and gas from EmissionsDetails
        emissions_data = asset.get('EmissionsDetails', [])
        year_emissions = [e for e in emissions_data if e.get('Year') == year and e.get('Gas') == gas]

        if year_emissions:
            emissions_quantity = sum(e.get('EmissionsQuantity', 0) for e in year_emissions)
        else:
            emissions_quantity = 0

        results.append({
            'source_id': asset.get('Id'),
            'source_name': asset.get('Name'),
            'source_type': asset.get('AssetType'),
            'iso3_country': asset.get('Country'),
            'subsector': asset.get('Sector'),
            'year': year,
            'gas': gas,
            'emissions_quantity': emissions_quantity
        })

    return pd.DataFrame(results)


if __name__ == '__main__':
    OWNER_NAME = 'Hwa Ya Power Corp'
    DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'ownership')
    INPUT_OWNERS_ASSETS = os.path.join(DATA_DIR, 'ownership.zip')

    owner_sources = find_owner_sources(OWNER_NAME, INPUT_OWNERS_ASSETS)
    owners_emissions = find_owners_emissions(owner_sources)

