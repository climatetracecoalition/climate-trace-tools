# Ownership

The Ownership tool allows you to look up asset ownership information and retrieve associated emissions data via the Climate TRACE API.

## Usage

```python
from climate_trace_tools import find_owner_sources, find_owners_emissions

# Step 1: Find source IDs for an owner (pass the zip or a CSV path)
source_ids = find_owner_sources('Hwa Ya Power Corp', 'climate_trace_tools/data/ownership/ownership.zip')

# Step 2: Get emissions for those sources
df = find_owners_emissions(source_ids, gas='co2e_100yr', year=2024)
```

## Functions

### `find_owner_sources(owner_name, ownership_file)`

Looks up Climate TRACE source IDs associated with a given asset owner.

**Parameters:**
- **owner_name**: Name of the asset owner to look up
- **ownership_file**: Path to the ownership CSV file or `ownership.zip` (bundled in `climate_trace_tools/data/ownership/`)

**Returns:** A list of unique source IDs associated with the owner.

### `find_owners_emissions(sources, gas, year)`

Fetches emissions for a list of source IDs using the Climate TRACE API.

**Parameters:**
- **sources**: A list of Climate TRACE source IDs
- **gas**: Gas of interest (default: `'co2e_100yr'`)
- **year**: Year of emissions data (default: 2024)

**Returns:** A DataFrame with asset details (source ID, name, type, country, subsector) and emissions data for the specified year and gas.

## Data

The ownership data is bundled as `ownership.zip` in `climate_trace_tools/data/ownership/`. The zip contains:
- `ownership_all_entity_asset_relationships_December_2025.csv` — maps asset owners to Climate TRACE source IDs
- `ownership_all_entities_September_2025.csv` — all ownership entities
- `ownership_all_entity_relationships_September_2025.csv` — entity relationship data

## Requirements

- Python packages: `pandas`, `requests`
- Access to the Climate TRACE API (`https://api.climatetrace.org/v6`)
