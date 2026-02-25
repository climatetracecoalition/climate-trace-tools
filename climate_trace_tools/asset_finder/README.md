# Asset Finder

The Asset Finder tool allows you to find Climate TRACE point assets within a given location and buffer zone radius, along with their emissions data and regional (GADM) benchmarks.

## Usage

```python
from climate_trace_tools import find_assets

# Find assets near a coordinate
df = find_assets('37.77, -122.42', buffer_zone=5, year=2024)

# Find assets within a polygon
df = find_assets('POLYGON((-122.42 37.77, -122.41 37.78, -122.40 37.77, -122.42 37.77))', buffer_zone=5)

# Filter by sector and country
df = find_assets('37.77, -122.42', sectors=['electricity-generation'], country='USA')
```

## Parameters

- **location**: Coordinates as a `'lat, lon'` string, or a WKT `POLYGON`/`MULTIPOLYGON` string
- **buffer_zone**: Radius in kilometers around the location to search (default: 5)
- **year**: Year of emissions data (default: 2024)
- **gas**: Gas of interest (default: `'co2e_100yr'`)
- **sectors**: Sectors to filter by — `'all'`, a comma-separated string, or a list (default: `'all'`)
- **country**: ISO3 country code to limit the search to a specific country (default: `None`)
- **asset_cols**: List of additional columns to include from the asset data tables (default: `None`)

## Output

Returns a DataFrame with:
- Asset details (source ID, name, type, subsector, location)
- Distance from the origin point
- Emissions data (quantity, activity, emissions factor)
- GADM-level benchmarks (gadm_0, gadm_1, gadm_2) for emissions within the same region and sector

## Authentication

This tool queries Climate TRACE data via Google BigQuery. For full details on access requirements, permissions, and getting started, see [BigQuery Data.md](./BigQuery%20Data.md).

## Requirements

- Google Cloud authentication (see above)
- Python packages: `pandas`, `shapely`, `geopy`, `google-cloud-bigquery`
