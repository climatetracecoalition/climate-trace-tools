# Asset Finder

The Asset Finder tool allows you to find Climate TRACE point assets within a given location and buffer zone radius, along with their emissions data and regional (GADM) benchmarks.

## Usage

```python
from climate_trace_tools import find_assets

# Find assets near a coordinate
df = find_assets('37.77, -122.42', buffer_zone=5, year=2025)

# Find assets within a polygon
df = find_assets('POLYGON((-122.42 37.77, -122.41 37.78, -122.40 37.77, -122.42 37.77))', buffer_zone=5)

# Filter by sector and country
df = find_assets('37.77, -122.42', sectors=['electricity-generation'], country='USA')
```

## Parameters

- **location**: Coordinates as a `'lat, lon'` string, or a WKT `POLYGON`/`MULTIPOLYGON` string
- **buffer_zone**: Radius in kilometers around the location to search (default: 5)
- **year**: Year of emissions data (default: 2025)
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

To authenticate locally, install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) and run:

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

Replace `YOUR_PROJECT_ID` with your own Google Cloud project ID.

## Tips for New Users

### Sectors and country codes

The `sectors` parameter uses Climate TRACE sector names (e.g. `'electricity-generation'`, `'road-transportation'`). The `country` parameter uses ISO3 codes (e.g. `'USA'`, `'GBR'`, `'BRA'`). You can use `InputHelper` from the compare module to browse available sector names:

```python
from climate_trace_tools import InputHelper
ih = InputHelper()
ih.sectors_available_to_plot_subtract_out(annex1=True)
```

### Authentication must be set up before use

`find_assets` queries BigQuery and will fail immediately if Google Cloud credentials are not configured. Run the following before using this function:

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

If you see a quota or permissions error, confirm that your project has the BigQuery API enabled and that you have been granted access to the Climate TRACE dataset. See [BigQuery Data.md](./BigQuery%20Data.md) for full details.

## Expected Costs

`find_assets` queries two large BigQuery tables on each call:

- **`emissions_sources`** (~340 GB) — queried once per country that the submitted geometry intersects
- **`gadm_emissions`** (~122 GB) — queried once per country for all GADM levels combined

At standard [BigQuery on-demand pricing](https://cloud.google.com/bigquery/pricing) of $5 per TB scanned, the **worst-case cost** for a single call intersecting one country is roughly **$2.30** (340 GB + 122 GB ≈ 462 GB × $0.005). A geometry spanning multiple countries multiplies that by the number of intersected countries.

The actual cost will be lower than this worst case due to table partitioning. You can check the estimated bytes scanned before running using the [BigQuery console query validator](https://cloud.google.com/bigquery/docs/best-practices-costs#avoid_using_select_).

To reduce costs:
- Always pass the `country` parameter when you know which country you are querying — this skips the country-detection query and limits the asset scan to a single country.
- Use the `sectors` parameter to filter to only the sectors you need.

## Requirements

- Google Cloud authentication (see above)
- Python packages: `pandas`, `shapely`, `geopy`, `google-cloud-bigquery`, `db-dtypes`
