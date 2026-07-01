"""Python client for the Climate TRACE API (v7).

Import the endpoint functions directly, e.g.::

    from climate_trace_tools.api import (
        get_aggregate_emissions,
        search_admins,
        list_gases,
    )
"""

from .client import (
    BASE_URL,
    # emissions & sources
    get_aggregate_emissions,
    get_sources,
    get_source,
    rank_countries,
    # admins
    search_admins,
    get_admin,
    get_admin_subdivisions,
    # cities
    search_cities,
    get_city,
    # owners
    search_owners,
    # definitions
    list_continents,
    get_continent,
    list_countries,
    get_country,
    list_country_groups,
    get_country_group,
    list_gases,
    list_sectors,
    get_sector,
    list_subsectors,
    get_subsector,
)

__all__ = [
    "BASE_URL",
    "get_aggregate_emissions",
    "get_sources",
    "get_source",
    "rank_countries",
    "search_admins",
    "get_admin",
    "get_admin_subdivisions",
    "search_cities",
    "get_city",
    "search_owners",
    "list_continents",
    "get_continent",
    "list_countries",
    "get_country",
    "list_country_groups",
    "get_country_group",
    "list_gases",
    "list_sectors",
    "get_sector",
    "list_subsectors",
    "get_subsector",
]
