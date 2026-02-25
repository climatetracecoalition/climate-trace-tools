# Ownership

The Ownership tool allows you to look up asset ownership information and retrieve associated emissions data via the Climate TRACE API. It supports both simple immediate-ownership lookups and full traversal of direct and indirect ownership chains via a network graph.

Original methodology and implementation by Anna Mowat, with thanks to Amy Kouch for support.

## Usage

### Simple immediate ownership lookup

```python
from climate_trace_tools import find_owner_sources, find_owners_emissions

# Step 1: Find source IDs for an owner (immediate ownership only)
source_ids = find_owner_sources('Hwa Ya Power Corp', 'climate_trace_tools/data/ownership/ownership.zip')

# Step 2: Get emissions for those sources
df = find_owners_emissions(source_ids, gas='co2e_100yr', year=2024)
```

### Full direct and indirect ownership lookup

```python
from climate_trace_tools import get_assets_owned_by_entity

# Returns all assets the entity owns directly or indirectly, with emissions data
df = get_assets_owned_by_entity('BlackRock Inc', 'climate_trace_tools/data/ownership/ownership.zip')
```

> Note: `get_assets_owned_by_entity` does not prorate emissions by ownership shareholding percentage.

## Understanding the Ownership Network

Ownership data is a network structure — entities own other entities, which in turn own assets. Representing this as a graph makes it fast to traverse indirect ownership chains.

If you are unfamiliar with the concept of a graph network, some real-world analogies include:

- **Social Networks**: Mapping friendships, followers, or family connections (e.g., Facebook friends, Twitter mentions)
- **Fraud Detection**: Identifying suspicious links between accounts, users, or transactions using shared details like phone numbers or addresses
- **Cybersecurity**: Visualizing attack paths or connections between compromised systems and attackers

In this tool, each entity and asset is a node, and each ownership relationship is a directed edge. `get_assets_owned_by_entity` traverses this graph from a given entity to find everything it owns — directly or through intermediate entities.

## Functions

### `find_owner_sources(owner_name, ownership_file)`

Looks up Climate TRACE source IDs associated with a given asset owner (immediate ownership only).

**Parameters:**
- **owner_name**: Name of the asset owner to look up
- **ownership_file**: Path to `ownership.zip` (bundled in `climate_trace_tools/data/ownership/`) or a CSV path

**Returns:** A list of unique source IDs associated with the owner.

---

### `find_owners_emissions(sources, gas, year)`

Fetches emissions for a list of source IDs using the Climate TRACE API.

**Parameters:**
- **sources**: A list of Climate TRACE source IDs
- **gas**: Gas of interest (default: `'co2e_100yr'`)
- **year**: Year of emissions data (default: 2024)

**Returns:** A DataFrame with asset details (source ID, name, type, country, subsector) and emissions data for the specified year and gas.

---

### `get_assets_owned_by_entity(entity_name, ownership_zip, gas, year)`

Traverses the full ownership network to find all assets an entity has direct and indirect ownership in, then fetches their emissions. Emissions are not prorated by ownership shareholding percentage.

**Parameters:**
- **entity_name**: Full name of the entity (e.g., `'BlackRock Inc'`)
- **ownership_zip**: Path to `ownership.zip`
- **gas**: Gas of interest (default: `'co2e_100yr'`)
- **year**: Year of emissions data (default: 2024)

**Returns:** A DataFrame with columns: `Owner Entity ID`, `Owner`, `source_id`, `source_name`, `source_sector`, `source_subsector`, and emissions data.

---

### `load_ownership_data(ownership_zip)`

Loads all three ownership DataFrames from the zip file.

**Returns:** Tuple of `(asset_to_owner_df, all_entities_df, all_entity_connections_df)`.

---

### `build_ownership_graph(all_entities_df, all_entity_connections_df, asset_to_owner_df)`

Builds a directed `networkx.DiGraph` from the three ownership DataFrames. Nodes are either entities (owners) or assets; edges represent ownership relationships.

**Returns:** `nx.DiGraph`

## Data

The ownership data is bundled as `ownership.zip` in `climate_trace_tools/data/ownership/`. The zip contains three CSVs:

- **`ownership_all_entity_asset_relationships_*.csv`** — all individual connections between immediate owners and assets, covering all sectors the ownership data currently includes
- **`ownership_all_entities_*.csv`** — all entities (owners) in the Climate TRACE database, sourced and managed by Global Energy Monitor's [Ownership team](https://globalenergymonitor.org/projects/global-energy-ownership-tracker/). This file is sector-agnostic and includes attributes such as:
  - Registration and headquarter country
  - Entity type
  - Organizational identifiers
  - Other and former names
- **`ownership_all_entity_relationships_*.csv`** — every known ownership connection between entities, including percent of ownership (where known) and the data source used to identify the connection

## Requirements

- Python packages: `pandas`, `requests`, `networkx`, `tqdm`
- Access to the Climate TRACE API (`https://api.climatetrace.org/v6`)
