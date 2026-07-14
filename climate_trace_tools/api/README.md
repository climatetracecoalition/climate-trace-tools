# Climate TRACE API client

A lightweight Python client for the public [Climate TRACE API](https://api.climatetrace.org/v7/docs/index.html) (v7). Each function wraps a single API endpoint and returns the parsed JSON response (a `dict` or `list`). No authentication is required.

For a runnable, worked walkthrough see the guide notebook: [`examples/climate_trace_api_guide.ipynb`](examples/climate_trace_api_guide.ipynb).

## Quick start

```python
from climate_trace_tools.api import (
    get_aggregate_emissions,
    get_aggregate_emissions_df,
)

# Total CO2 emissions for Denmark in 2023.
# A country's gadm_id is simply its ISO3 code — no lookup needed.
get_aggregate_emissions(gadm_id="DNK", year=2023, gas="co2")

# Same query as a tidy pandas DataFrame (one row per total/sector/subsector).
get_aggregate_emissions_df(gadm_id="DNK", year=2023, gas="co2")
```

## Conventions

- **Return values** are the raw decoded JSON from the API (`dict` or `list`) — no wrapper objects. The [`*_df` helpers](#pandas-dataframe-helpers) return pandas DataFrames instead.
- **Errors**: a non-2xx response raises `requests.HTTPError`.
- **List filters** (`sectors`, `subsectors`, `owner_ids`) accept either a Python list (`["agriculture", "power"]`) or a comma-separated string (`"agriculture,power"`).
- **`None` arguments are omitted** from the request, so you only pass the filters you care about.
- **Reference/`list_*` endpoints** (gases, sectors, continents, ...) tell you the valid values to use in filters.
- **Targeting staging/dev**: set `climate_trace_tools.api.client.BASE_URL`, or pass `base_url=...` to the underlying `_get` helper.

## Common filter parameters

These parameters are shared by many functions and referenced throughout the [endpoint reference](#endpoint-reference) below.

| Parameter | Type | Meaning |
| --- | --- | --- |
| `year` | int | Emissions year to query, e.g. `2023`. |
| `gas` | str | Gas code, e.g. `"co2"`, `"ch4"`, `"n2o"`, or the CO2-equivalent aggregates `"co2e_100yr"` / `"co2e_20yr"` — these five cover most analyses. `list_gases()` returns the full list of accepted codes, but many of the others have little or no data in Climate TRACE and return zero emissions. |
| `sectors` / `subsectors` | list or str | Restrict to these sectors/subsectors. Valid values from `list_sectors()` / `list_subsectors()`, e.g. `"power"`, `"agriculture"`. |
| `gadm_id` | str | Administrative area id. **For a country this is simply its ISO3 code** (`"DNK"` for Denmark) — no lookup needed. For subnational areas (states, districts, ...) the ids look like `"USA.5_1"`; find them with `search_admins()`. |
| `city_id` | str | City / functional urban area id from `search_cities()`. |
| `country_group` | str | Country group id from `list_country_groups()`, e.g. `"unfccc_annex1"`, `"unfccc_nonannex1"`, `"eu"`, `"oecd"`, `"g20"`, `"opec"`. |
| `continent` | str | Continent name from `list_continents()`, e.g. `"North America"`. |
| `owner_ids` | list or str | Restrict to assets held by these owners; ids from `search_owners()`. |
| `start` / `end` | str | Time range bounds (`rank_countries`, `get_source`). Accept a year (`"2025"`), month (`"2025-01"`), or day (`"2025-01-31"`). |
| `bbox` | str | Geographic bounding box that results must fall within, as a comma-separated string `"minLon,minLat,maxLon,maxLat"` in WGS84 degrees — e.g. `"8.0,54.5,13.0,57.8"` roughly covers Denmark. |
| `limit` | int | Maximum number of results to return in one call. |
| `offset` | int | Number of results to skip before returning any — combine with `limit` to page through long result sets (e.g. `limit=100, offset=100` returns results 101–200). |

Every function also accepts arbitrary extra `**kwargs`, which are passed through as query parameters — handy if the API adds new parameters before this client is updated.

## Endpoint reference

### Emissions & sources

| Function | Endpoint | Description |
| --- | --- | --- |
| `get_aggregate_emissions(year, gas, sectors, subsectors, gadm_id, city_id, country_group, continent, owner_ids)` | `GET /v7/sources/emissions` | Aggregate emissions totals for a filtered slice of the data. |
| `get_sources(year, gas, sectors, subsectors, gadm_id, city_id, country_group, continent, owner_ids, limit, offset)` | `GET /v7/sources` | Individual emissions sources (assets) ranked by emissions. |
| `get_source(source_id, start, end, time_granularity, gas)` | `GET /v7/sources/{id}` | One source by id, with an emissions time series. |
| `rank_countries(gas, start, end, sectors, subsectors, country_group, continent)` | `GET /v7/rankings/countries` | Rank countries by emissions over a time range. |

### Administrative areas

| Function | Endpoint | Description |
| --- | --- | --- |
| `search_admins(name, bbox, level, limit, offset)` | `GET /v7/admins` | Search admin areas by name and/or [bounding box](#common-filter-parameters) (countries `level=0`, states `1`, districts `2`, ...). |
| `get_admin(admin_id)` | `GET /v7/admins/{id}` | An administrative area by id. |
| `get_admin_subdivisions(admin_id)` | `GET /v7/admins/{id}/subdivisions` | Child subdivisions of an admin area. |

### Cities

| Function | Endpoint | Description |
| --- | --- | --- |
| `search_cities(name, country, bbox, limit, offset)` | `GET /v7/cities` | Search cities / functional urban areas by name, ISO3 country code, and/or [bounding box](#common-filter-parameters). |
| `get_city(city_id)` | `GET /v7/cities/{id}` | A city by id. |

### Owners

| Function | Endpoint | Description |
| --- | --- | --- |
| `search_owners(name, limit, offset)` | `GET /v7/owners` | Search asset owners by (part of) their name. |

### Definitions (valid values for filters)

| Function | Endpoint | Description |
| --- | --- | --- |
| `list_continents()` | `GET /v7/definitions/continents` | All continent names, e.g. `"Europe"`, `"North America"`. |
| `get_continent(continent)` | `GET /v7/definitions/continents/{continent}` | One continent, with the ISO3 codes of every country in it. |
| `list_countries()` | `GET /v7/definitions/countries` | All countries: ISO3 code, name and continent. |
| `get_country(country)` | `GET /v7/definitions/countries/{country}` | One country by ISO3 code. |
| `list_country_groups()` | `GET /v7/definitions/countrygroups` | All country groups and their member countries (as ISO3 codes) — covers UNFCCC Annex 1 (`unfccc_annex1`) vs Non-Annex 1 (`unfccc_nonannex1`) plus other groupings like `eu`, `oecd`, `g7`, `g20`, `g77`, `opec`, `ldc`. |
| `get_country_group(group)` | `GET /v7/definitions/countrygroups/{group}` | One country group and its member countries. |
| `list_gases()` | `GET /v7/definitions/gases` | All gas codes accepted by the `gas` filter. Prefer `co2`, `ch4`, `n2o`, `co2e_100yr` or `co2e_20yr` — see [`gas`](#common-filter-parameters). |
| `list_sectors()` | `GET /v7/definitions/sectors` | All sectors. |
| `get_sector(sector)` | `GET /v7/definitions/sectors/{sector}` | One sector. |
| `list_subsectors()` | `GET /v7/definitions/subsectors` | All subsectors. |
| `get_subsector(subsector)` | `GET /v7/definitions/subsectors/{subsector}` | One subsector. |

## Pandas DataFrame helpers

For easier viewing and analysis, each of the main query functions has a `_df` twin that takes the same arguments but returns a `pandas.DataFrame` instead of raw JSON:

| Function | Wraps | Rows |
| --- | --- | --- |
| `get_aggregate_emissions_df(...)` | `get_aggregate_emissions` | One row per total / sector / subsector summary, with columns `level`, `sector`, `subsector`, `gas`, `emissions_quantity`, `percentage`. |
| `get_sources_df(...)` | `get_sources` | One row per emissions source, nested fields flattened into dotted columns (e.g. `centroid.latitude`). |
| `rank_countries_df(...)` | `rank_countries` | One row per country, ordered by rank. |

```python
from climate_trace_tools.api import get_aggregate_emissions_df

df = get_aggregate_emissions_df(gadm_id="DNK", year=2023, gas="co2")
df[df.level == "sector"].sort_values("emissions_quantity", ascending=False)
```
