# Climate TRACE API client

A lightweight Python client for the public [Climate TRACE API](https://api.climatetrace.org/v7/docs/index.html) (v7). Each function wraps a single API endpoint and returns the parsed JSON response (a `dict` or `list`). No authentication is required.

For a runnable, worked walkthrough see the guide notebook: [`examples/climate_trace_api_guide.ipynb`](examples/climate_trace_api_guide.ipynb).

## Quick start

```python
from climate_trace_tools.api import (
    get_aggregate_emissions,
    search_admins,
    list_gases,
)

# What gases can I query?
list_gases()  # ['bc', 'ch4', 'co2', 'co2e_100yr', ...]

# Look up an administrative area to get its id (aka gadmId).
# Search always returns a list, even for a single result.
denmark = search_admins(name="Denmark", level=0)[0]

# Total CO2 emissions for Denmark in 2023.
get_aggregate_emissions(gadm_id=denmark["id"], year=2023, gas="co2")
```

## Conventions

- **Return values** are the raw decoded JSON from the API (`dict` or `list`) — no wrapper objects.
- **Errors**: a non-2xx response raises `requests.HTTPError`.
- **List filters** (`sectors`, `subsectors`, `owner_ids`) accept either a Python list (`["agriculture", "power"]`) or a comma-separated string (`"agriculture,power"`).
- **`None` arguments are omitted** from the request, so you only pass the filters you care about.
- **Reference/`list_*` endpoints** (gases, sectors, continents, ...) tell you the valid values to use in filters.
- **Targeting staging/dev**: set `climate_trace_tools.api.client.BASE_URL`, or pass `base_url=...` to the underlying `_get` helper.

## Endpoint reference

### Emissions & sources

| Function | Endpoint | Description |
| --- | --- | --- |
| `get_aggregate_emissions(year, gas, sectors, subsectors, gadm_id, city_id, country_group, continent, owner_ids)` | `GET /v7/sources/emissions` | Aggregate emissions totals for a filtered slice of the data. |
| `get_sources(... same filters ..., limit, offset)` | `GET /v7/sources` | Individual emissions sources (assets) ranked by emissions. |
| `get_source(source_id, start, end, time_granularity, gas)` | `GET /v7/sources/{id}` | One source by id, with an emissions time series. |
| `rank_countries(gas, start, end, sectors, subsectors, country_group, continent)` | `GET /v7/rankings/countries` | Rank countries by emissions over a time range. |

### Administrative areas

| Function | Endpoint | Description |
| --- | --- | --- |
| `search_admins(name, bbox, level, limit, offset)` | `GET /v7/admins` | Search admin areas (countries `level=0`, states `1`, districts `2`, ...). |
| `get_admin(admin_id)` | `GET /v7/admins/{id}` | An administrative area by id. |
| `get_admin_subdivisions(admin_id)` | `GET /v7/admins/{id}/subdivisions` | Child subdivisions of an admin area. |

### Cities

| Function | Endpoint | Description |
| --- | --- | --- |
| `search_cities(name, country, bbox, limit, offset)` | `GET /v7/cities` | Search cities / functional urban areas. |
| `get_city(city_id)` | `GET /v7/cities/{id}` | A city by id. |

### Owners

| Function | Endpoint | Description |
| --- | --- | --- |
| `search_owners(name, limit, offset)` | `GET /v7/owners` | Search asset owners. |

### Definitions (valid values for filters)

| Function | Endpoint | Description |
| --- | --- | --- |
| `list_continents()` | `GET /v7/definitions/continents` | All continents. |
| `get_continent(continent)` | `GET /v7/definitions/continents/{continent}` | One continent. |
| `list_countries()` | `GET /v7/definitions/countries` | All countries. |
| `get_country(country)` | `GET /v7/definitions/countries/{country}` | One country by ISO3 code. |
| `list_country_groups()` | `GET /v7/definitions/countrygroups` | All country groups. |
| `get_country_group(group)` | `GET /v7/definitions/countrygroups/{group}` | One country group. |
| `list_gases()` | `GET /v7/definitions/gases` | All supported gases. |
| `list_sectors()` | `GET /v7/definitions/sectors` | All sectors. |
| `get_sector(sector)` | `GET /v7/definitions/sectors/{sector}` | One sector. |
| `list_subsectors()` | `GET /v7/definitions/subsectors` | All subsectors. |
| `get_subsector(subsector)` | `GET /v7/definitions/subsectors/{subsector}` | One subsector. |

## Common filter parameters

Shared by `get_aggregate_emissions`, `get_sources` and (a subset by) `rank_countries`:

| Parameter | Type | Notes |
| --- | --- | --- |
| `year` | int | Emissions year, e.g. `2023`. |
| `gas` | str | Gas code from `list_gases()`, e.g. `"co2"`, `"ch4"`, `"co2e_100yr"`. |
| `sectors` / `subsectors` | list or str | Values from `list_sectors()` / `list_subsectors()`. |
| `gadm_id` | str | Admin area id from `search_admins()`. |
| `city_id` | str | City id from `search_cities()`. |
| `country_group` | str | Group id from `list_country_groups()`. |
| `continent` | str | Continent name from `list_continents()`, e.g. `"North America"`. |
| `owner_ids` | list or str | Owner ids from `search_owners()`. |
| `start` / `end` | str | Time range (`rank_countries`, `get_source`). Supports `"2025"`, `"2025-01"`, `"2025-01-31"`. |
| `limit` / `offset` | int | Pagination (`get_sources`, and the search endpoints). |

Every function also accepts arbitrary extra `**kwargs`, which are passed through as query parameters — handy if the API adds new parameters before this client is updated.
