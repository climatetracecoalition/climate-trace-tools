"""Simple Python client for the Climate TRACE API (v7).

Each function wraps a single endpoint of the public Climate TRACE API and
returns the parsed JSON response. No authentication is required.

API docs: https://api.climatetrace.org/v7/docs/index.html
OpenAPI spec: bundled in this repo as ``api-1.json``.

Example
-------
>>> from climate_trace_tools.api import get_aggregate_emissions
>>> # A country's gadm_id is simply its ISO3 code.
>>> get_aggregate_emissions(gadm_id="DNK", year=2023, gas="co2")
"""

import requests

# Base URL for the production Climate TRACE API.
# Override to target staging/development, e.g.
# "https://api.staging.c10e.org/v7" or "https://api.dev.c10e.org/v7".
BASE_URL = "https://api.climatetrace.org/v7"

# Default timeout (seconds) for every request.
DEFAULT_TIMEOUT = 30


def _to_csv(value):
    """Coerce a list/tuple into the comma-separated string the API expects.

    Passing a plain string through unchanged lets callers supply either
    ``["agriculture", "power"]`` or ``"agriculture,power"``.
    """
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return ",".join(str(v) for v in value)
    return value


def _get(endpoint, params=None, base_url=None, timeout=DEFAULT_TIMEOUT):
    """Send a GET request to the API and return the parsed JSON.

    Parameters
    ----------
    endpoint : str
        Path beginning with "/", e.g. "/sources/emissions".
    params : dict, optional
        Query parameters. Keys whose value is ``None`` are dropped.
    base_url : str, optional
        Override :data:`BASE_URL` for this call (e.g. to hit staging).
    timeout : int, optional
        Request timeout in seconds.

    Returns
    -------
    dict or list
        The decoded JSON response.

    Raises
    ------
    requests.HTTPError
        If the API returns a non-2xx status code.
    """
    url = f"{base_url or BASE_URL}{endpoint}"
    clean_params = {k: v for k, v in (params or {}).items() if v is not None}
    response = requests.get(url, params=clean_params, timeout=timeout)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Emissions & sources
# ---------------------------------------------------------------------------


def get_aggregate_emissions(
    year=None,
    gas=None,
    sectors=None,
    subsectors=None,
    gadm_id=None,
    city_id=None,
    country_group=None,
    continent=None,
    owner_ids=None,
    **kwargs,
):
    """Aggregate emissions totals for a filtered slice of the data.

    Endpoint: ``GET /v7/sources/emissions``

    Parameters
    ----------
    year : int, optional
        Emissions year.
    gas : str, optional
        Gas code, e.g. "co2", "ch4", "co2e_100yr". See :func:`list_gases`.
    sectors, subsectors : str or list of str, optional
        Sector/subsector filters. See :func:`list_sectors` / :func:`list_subsectors`.
    gadm_id : str, optional
        Administrative area id. For a country this is simply its ISO3 code
        (e.g. "DNK" for Denmark); for subnational areas (states, districts,
        ...) find the id with :func:`search_admins`.
    city_id : str, optional
        City / urban area id (from :func:`search_cities`).
    country_group : str, optional
        Country group id. See :func:`list_country_groups`.
    continent : str, optional
        Continent name. See :func:`list_continents`.
    owner_ids : str or list of str, optional
        Owner ids (from :func:`search_owners`).

    Returns
    -------
    dict
        Aggregated emissions totals and summaries.
    """
    params = {
        "year": year,
        "gas": gas,
        "sectors": _to_csv(sectors),
        "subsectors": _to_csv(subsectors),
        "gadmId": gadm_id,
        "cityId": city_id,
        "countryGroup": country_group,
        "continent": continent,
        "ownerIds": _to_csv(owner_ids),
        **kwargs,
    }
    return _get("/sources/emissions", params)


def get_sources(
    year=None,
    gas=None,
    sectors=None,
    subsectors=None,
    gadm_id=None,
    city_id=None,
    country_group=None,
    continent=None,
    owner_ids=None,
    limit=None,
    offset=None,
    **kwargs,
):
    """List individual emissions sources (assets), ranked by emissions.

    Endpoint: ``GET /v7/sources``

    Accepts the same filters as :func:`get_aggregate_emissions` (``year``,
    ``gas``, ``sectors``, ``subsectors``, ``gadm_id``, ``city_id``,
    ``country_group``, ``continent``, ``owner_ids``), plus ``limit`` (max
    results per call) and ``offset`` (number of results to skip) for
    pagination.

    Returns
    -------
    list
        Sources matching the filters, ranked by emissions.
    """
    params = {
        "year": year,
        "gas": gas,
        "sectors": _to_csv(sectors),
        "subsectors": _to_csv(subsectors),
        "gadmId": gadm_id,
        "cityId": city_id,
        "countryGroup": country_group,
        "continent": continent,
        "ownerIds": _to_csv(owner_ids),
        "limit": limit,
        "offset": offset,
        **kwargs,
    }
    return _get("/sources", params)


def get_source(source_id, start=None, end=None, time_granularity=None, gas=None, **kwargs):
    """Fetch a single emissions source by its id.

    Endpoint: ``GET /v7/sources/{id}``

    Parameters
    ----------
    source_id : int or str
        The source id.
    start, end : str, optional
        Time range bounds (minimum "2021-01-01"). Supports year ("2025"),
        month ("2025-01") or day ("2025-01-31") granularity.
    time_granularity : str, optional
        Unit for aggregating emissions over the range (e.g. "year", "month").
    gas : str, optional
        Gas code. See :func:`list_gases`.

    Returns
    -------
    dict
        Details and emissions time series for the source.
    """
    params = {
        "start": start,
        "end": end,
        "timeGranularity": time_granularity,
        "gas": gas,
        **kwargs,
    }
    return _get(f"/sources/{source_id}", params)


def rank_countries(
    gas=None,
    start=None,
    end=None,
    sectors=None,
    subsectors=None,
    country_group=None,
    continent=None,
    **kwargs,
):
    """Rank countries by emissions over a time range.

    Endpoint: ``GET /v7/rankings/countries``

    Parameters
    ----------
    gas : str, optional
        Gas code. See :func:`list_gases`.
    start, end : str, optional
        Time range bounds. Supports year ("2025"), month ("2025-01") or
        day ("2025-01-31") granularity.
    sectors, subsectors : str or list of str, optional
        Sector/subsector filters.
    country_group : str, optional
        Country group id. See :func:`list_country_groups`.
    continent : str, optional
        Continent name. See :func:`list_continents`.

    Returns
    -------
    dict
        Countries ranked by emissions.
    """
    params = {
        "gas": gas,
        "start": start,
        "end": end,
        "sectors": _to_csv(sectors),
        "subsectors": _to_csv(subsectors),
        "countryGroup": country_group,
        "continent": continent,
        **kwargs,
    }
    return _get("/rankings/countries", params)


# ---------------------------------------------------------------------------
# Administrative areas
# ---------------------------------------------------------------------------


def search_admins(name=None, bbox=None, level=None, limit=None, offset=None, **kwargs):
    """Search administrative areas (countries, states, districts, ...).

    Endpoint: ``GET /v7/admins``

    Parameters
    ----------
    name : str, optional
        Any part of an administrative area's name.
    bbox : str, optional
        Bounding box filter, format "minX,minY,maxX,maxY".
    level : int, optional
        Subdivision depth: countries = 0, states = 1, districts = 2, ...
    limit, offset : int, optional
        Pagination controls.

    Returns
    -------
    list
        Matching administrative areas (always a list, even for one result).
    """
    params = {
        "name": name,
        "bbox": bbox,
        "level": level,
        "limit": limit,
        "offset": offset,
        **kwargs,
    }
    return _get("/admins", params)


def get_admin(admin_id, **kwargs):
    """Fetch an administrative area by id.

    Endpoint: ``GET /v7/admins/{id}``
    """
    return _get(f"/admins/{admin_id}", kwargs or None)


def get_admin_subdivisions(admin_id, **kwargs):
    """List the child subdivisions of an administrative area.

    Endpoint: ``GET /v7/admins/{id}/subdivisions``
    """
    return _get(f"/admins/{admin_id}/subdivisions", kwargs or None)


# ---------------------------------------------------------------------------
# Cities
# ---------------------------------------------------------------------------


def search_cities(name=None, country=None, bbox=None, limit=None, offset=None, **kwargs):
    """Search cities / functional urban areas.

    Endpoint: ``GET /v7/cities``

    Parameters
    ----------
    name : str, optional
        Any part of a city name.
    country : str, optional
        3-letter (ISO3) country code.
    bbox : str, optional
        Bounding box filter, format "minX,minY,maxX,maxY".
    limit, offset : int, optional
        Pagination controls.

    Returns
    -------
    list
        Matching cities.
    """
    params = {
        "name": name,
        "country": country,
        "bbox": bbox,
        "limit": limit,
        "offset": offset,
        **kwargs,
    }
    return _get("/cities", params)


def get_city(city_id, **kwargs):
    """Fetch a city / functional urban area by id.

    Endpoint: ``GET /v7/cities/{id}``
    """
    return _get(f"/cities/{city_id}", kwargs or None)


# ---------------------------------------------------------------------------
# Owners
# ---------------------------------------------------------------------------


def search_owners(name=None, limit=None, offset=None, **kwargs):
    """Search asset owners.

    Endpoint: ``GET /v7/owners``

    Parameters
    ----------
    name : str, optional
        Any part of an owner's name.
    limit, offset : int, optional
        Pagination controls.

    Returns
    -------
    list
        Matching owners.
    """
    params = {"name": name, "limit": limit, "offset": offset, **kwargs}
    return _get("/owners", params)


# ---------------------------------------------------------------------------
# Definitions (reference data for valid filter values)
# ---------------------------------------------------------------------------


def list_continents(**kwargs):
    """List all continents. Endpoint: ``GET /v7/definitions/continents``"""
    return _get("/definitions/continents", kwargs or None)


def get_continent(continent, **kwargs):
    """Details for one continent. Endpoint: ``GET /v7/definitions/continents/{continent}``"""
    return _get(f"/definitions/continents/{continent}", kwargs or None)


def list_countries(**kwargs):
    """List all countries. Endpoint: ``GET /v7/definitions/countries``"""
    return _get("/definitions/countries", kwargs or None)


def get_country(country, **kwargs):
    """Details for one country by ISO3 code. Endpoint: ``GET /v7/definitions/countries/{country}``"""
    return _get(f"/definitions/countries/{country}", kwargs or None)


def list_country_groups(**kwargs):
    """List all country groups. Endpoint: ``GET /v7/definitions/countrygroups``"""
    return _get("/definitions/countrygroups", kwargs or None)


def get_country_group(group, **kwargs):
    """Details for one country group. Endpoint: ``GET /v7/definitions/countrygroups/{group}``"""
    return _get(f"/definitions/countrygroups/{group}", kwargs or None)


def list_gases(**kwargs):
    """List all gas codes accepted by the ``gas`` filter.

    Endpoint: ``GET /v7/definitions/gases``

    Note: the list is long, but most analyses should use ``"co2"``,
    ``"ch4"``, ``"n2o"``, or the CO2-equivalent aggregates
    ``"co2e_100yr"`` / ``"co2e_20yr"``. Many of the other codes have
    little or no data in Climate TRACE and return zero emissions.
    """
    return _get("/definitions/gases", kwargs or None)


def list_sectors(**kwargs):
    """List all sectors. Endpoint: ``GET /v7/definitions/sectors``"""
    return _get("/definitions/sectors", kwargs or None)


def get_sector(sector, **kwargs):
    """Details for one sector. Endpoint: ``GET /v7/definitions/sectors/{sector}``"""
    return _get(f"/definitions/sectors/{sector}", kwargs or None)


def list_subsectors(**kwargs):
    """List all subsectors. Endpoint: ``GET /v7/definitions/subsectors``"""
    return _get("/definitions/subsectors", kwargs or None)


def get_subsector(subsector, **kwargs):
    """Details for one subsector. Endpoint: ``GET /v7/definitions/subsectors/{subsector}``"""
    return _get(f"/definitions/subsectors/{subsector}", kwargs or None)


# ---------------------------------------------------------------------------
# Pandas DataFrame helpers
# ---------------------------------------------------------------------------


def get_aggregate_emissions_df(**filters):
    """Aggregate emissions as a tidy :class:`pandas.DataFrame`.

    Accepts the same arguments as :func:`get_aggregate_emissions` and
    flattens the annual summaries into one row per total / sector /
    subsector, with columns ``level``, ``sector``, ``subsector``, ``gas``,
    ``emissions_quantity`` and ``percentage``.
    """
    import pandas as pd

    data = get_aggregate_emissions(**filters)
    rows = []
    for group in ("totals", "sectors", "subsectors"):
        for item in (data.get(group) or {}).get("summaries") or []:
            rows.append(
                {
                    "level": group.rstrip("s"),  # total / sector / subsector
                    "sector": item.get("sector"),
                    "subsector": item.get("subsector"),
                    "gas": item.get("gas"),
                    "emissions_quantity": item.get("emissionsQuantity"),
                    "percentage": item.get("percentage"),
                }
            )
    return pd.DataFrame(rows)


def get_sources_df(**filters):
    """Individual emissions sources as a :class:`pandas.DataFrame`.

    Accepts the same arguments as :func:`get_sources`; one row per source,
    with nested fields (e.g. the centroid coordinates) flattened into
    dotted columns.
    """
    import pandas as pd

    return pd.json_normalize(get_sources(**filters))


def rank_countries_df(**filters):
    """Country emissions rankings as a :class:`pandas.DataFrame`.

    Accepts the same arguments as :func:`rank_countries`; one row per
    country, ordered by rank.
    """
    import pandas as pd

    return pd.DataFrame(rank_countries(**filters).get("rankings") or [])
