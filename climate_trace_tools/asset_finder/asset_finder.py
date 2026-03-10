import pandas as pd
from shapely import wkt
from shapely.geometry import Point, Polygon
from geopy.distance import geodesic
from google.cloud import bigquery

client = bigquery.Client(project="trace-data-383422")


def run_bigquery(sql_query):
    query_job = client.query(sql_query)
    df = query_job.to_dataframe(create_bqstorage_client=False)
    return df


def find_assets(
    location,
    buffer_zone=5,
    year=2025,
    gas="co2e_100yr",
    sectors="all",
    country=None,
    asset_cols=None,
):
    """
    finds point assets within a certain buffer_zone radius of a location
    parameters:
        location: coordinates in a lat-lon string: '37.77, -122.42' or
                  polygon shape of region: 'POLYGON((-122.42 37.77, -122.41 37.78, -122.40 37.77, -122.42 37.77))'
        buffer_zone: numeric value in kilometers representing approx radius/buffer of interest from provided location
        year: year of interest of emission data (default: 2025)
        gas: gas of interest
        sectors: sectors of interest in list. example: ['electricity-generation']
        country: specific country of interest in iso3_country format
        asset_cols: list of additional columns to include from asset_emissions data table, with prefix "ae." "ai." or "al."
    returns:
        dataframe with nearby point assets, their emissions data, and gadm_0, gadm_1, and gadm_2 benchmarks
    """

    FINAL_COLS = [
        "location",
        "origin",
        "source_id",
        "source_name",
        "source_type",
        "iso3_country",
        "source_lat_lon",
        "source_km_from_origin",
        "buffer",
        "subsector",
        "year",
        "num_months",
        "gas",
        "activity",
        "activity_units",
        "emissions_quantity",
        "emissions_factor",
        "emissions_factor_units",
        "gadm_0",
        "gadm_0_name",
        "gadm_0_activity",
        "gadm_0_emissions_quantity",
        "gadm_0_emissions_factor",
        "gadm_1",
        "gadm_1_name",
        "gadm_1_activity",
        "gadm_1_emissions_quantity",
        "gadm_1_emissions_factor",
        "gadm_2",
        "gadm_2_name",
        "gadm_2_activity",
        "gadm_2_emissions_quantity",
        "gadm_2_emissions_factor",
    ]

    location = str(location)

    # determine location type
    if location.strip().upper().startswith(("POLYGON", "MULTIPOLYGON")):
        location_type = "area"
        location = location.strip()
        origin = wkt.loads(location).centroid
    else:
        # parse lat, lon from string
        try:
            lat_str, lon_str = location.split(",")
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            # validate ranges
            assert -90 <= lat <= 90, f"Latitude {lat} out of range."
            assert -180 <= lon <= 180, f"Longitude {lon} out of range."
            location_type = "coordinate"
            origin = Point(lon, lat)
        except Exception as e:
            raise ValueError(
                f"Invalid location string format: '{location}'. Must be 'lat, lon' or POLYGON. Error: {e}"
            )
    print("\n***")
    print(location)
    print("Origin (centroid) is  %s" % origin)

    # check subsector
    all_sectors = [
        "cropland-fires",
        "crop-residues",
        "enteric-fermentation-cattle-operation",
        "enteric-fermentation-cattle-pasture",
        "enteric-fermentation-other",
        "manure-applied-to-soils",
        "manure-left-on-pasture-cattle",
        "manure-management-cattle-operation",
        "manure-management-other",
        "other-agricultural-soil-emissions",
        "rice-cultivation",
        "synthetic-fertilizer-application",
        "non-residential-onsite-fuel-usage",
        "other-onsite-fuel-usage",
        "residential-onsite-fuel-usage",
        "fluorinated-gases",
        "forest-land-clearing",
        "forest-land-degradation",
        "forest-land-fires",
        "net-forest-land",
        "net-shrubgrass",
        "net-wetland",
        "removals",
        "shrubgrass-fires",
        "water-reservoirs",
        "wetland-fires",
        "coal-mining",
        "oil-and-gas-production",
        "oil-and-gas-refining",
        "oil-and-gas-transport",
        "other-fossil-fuel-operations",
        "other-solid-fuels",
        "aluminum",
        "cement",
        "chemicals",
        "food-beverage-tobacco",
        "glass",
        "iron-and-steel",
        "lime",
        "other-chemicals",
        "other-manufacturing",
        "other-metals",
        "petrochemical-steam-cracking",
        "pulp-and-paper",
        "textiles-leather-apparel",
        "wood-and-wood-products",
        "bauxite-mining",
        "copper-mining",
        "iron-mining",
        "other-mining-quarrying",
        "rock-quarrying",
        "sand-quarrying",
        "electricity-generation",
        "heat-plants",
        "other-energy-use",
        "domestic-aviation",
        "domestic-shipping",
        "domestic-shipping-ship",
        "international-aviation",
        "international-shipping",
        "international-shipping-ship",
        "non-broadcasting-vessels",
        "other-transport",
        "railways",
        "road-transportation",
        "road-transportation-road-segment",
        "biological-treatment-of-solid-waste-and-biogenic",
        "domestic-wastewater-treatment-and-discharge",
        "incineration-and-open-burning-of-waste",
        "industrial-wastewater-treatment-and-discharge",
        "solid-waste-disposal",
    ]
    if isinstance(sectors, str):
        if sectors.strip().lower() == "all":
            sectors = all_sectors
        else:
            sectors_defined = [s.strip() for s in sectors.split(",")]
            invalid_sectors = [s for s in sectors_defined if s not in all_sectors]
            if invalid_sectors:
                raise ValueError(
                    f"Invalid sector name(s): {', '.join(invalid_sectors)}"
                )
            sectors = sectors_defined
    elif isinstance(sectors, (list, tuple)):
        invalid_sectors = [s for s in sectors if s not in all_sectors]
        if invalid_sectors:
            raise ValueError(f"Invalid sector name(s): {', '.join(invalid_sectors)}")
    else:
        raise ValueError("Invalid type for sectors. Expected string or list.")

    sectors_str = "(" + ", ".join(f"'{s}'" for s in sectors) + ")"

    # find countries relevant to the analysis
    if location_type == "coordinate":
        location_zone = f"ST_GEOGPOINT({lon}, {lat})"
        buffer_zone_geom = (
            f"ST_Buffer(ST_GEOGPOINT({lon}, {lat}), {buffer_zone} * 1000)"
        )

    elif location_type == "area":
        location_zone = f"ST_GEOGFROMTEXT('{location}')"
        buffer_zone_geom = (
            f"ST_Buffer(ST_GEOGFROMTEXT('{location}'), {buffer_zone} * 1000)"
        )

    if country is not None:
        countries = [country]
    else:
        query_countries = f"""
            SELECT DISTINCT iso3_country
            FROM `trace-data-383422.climate_trace.geometries`
            WHERE ST_DWithin(boundary, {location_zone}, 0)
        """

        countries = run_bigquery(query_countries)
        assert (
            not countries.empty
        ), "Location exists outside of the boundaries of Climate Trace data"
        countries = countries["iso3_country"].unique()

    asset_df = pd.DataFrame()
    for country in countries:
        print("\nChecking assets in %s" % country)
        if asset_cols is None:
            query_assets = f"""
            SELECT
                es.source_id,
                es.source_name,
                es.source_type,
                es.subsector,
                ANY_VALUE(esl.location_geog) AS source_lat_lon,
                es.iso3_country,
                esl.gadm_0,
                esl.gadm_1,
                esl.gadm_2,
                EXTRACT(YEAR FROM es.start_time) AS year,
                COUNT(es.start_time) AS num_months,
                es.gas,
                SUM(es.emissions_quantity) AS emissions_quantity,
                es.emissions_factor_units,
                SUM(es.capacity) AS capacity,
                SUM(es.activity) AS activity,
                es.activity_units,
                CASE 
                    WHEN ST_DWithin(ANY_VALUE(esl.location_geog), {location_zone}, 0) THEN FALSE
                    WHEN ST_DWithin(ANY_VALUE(esl.location_geog), {buffer_zone_geom}, 0) THEN TRUE
                    ELSE FALSE
                END AS buffer
            FROM `trace-data-383422.climate_trace.emissions_sources` es
            LEFT JOIN `trace-data-383422.climate_trace.emissions_sources_location` esl
                ON es.source_id = esl.source_id
            WHERE
                es.gas = '{gas}'
                AND es.iso3_country = '{country}'
                AND es.start_time >= '{year}-01-01' AND es.start_time < '{year + 1}-01-01'
                AND es.subsector IN {sectors_str}
            GROUP BY
                es.source_id,
                es.source_name,
                es.source_type,
                es.subsector,
                es.iso3_country,
                esl.gadm_0,
                esl.gadm_1,
                esl.gadm_2,
                EXTRACT(YEAR FROM es.start_time),
                es.emissions_factor_units,
                es.activity_units,
                es.gas
            HAVING 
                (
                    ST_DWithin(ANY_VALUE(esl.location_geog), {location_zone}, 0)
                    OR (
                        ST_DWithin(ANY_VALUE(esl.location_geog), {buffer_zone_geom}, 0)
                        AND NOT ST_DWithin(ANY_VALUE(esl.location_geog), {location_zone}, 0)
                    )
                )
            ;
            """
        else:
            # if asset_cols are included, update the sql query + final columns
            new_cols_sql = ", ".join(asset_cols)
            new_cols = [c.split(".", 1)[1] for c in asset_cols]
            FINAL_COLS.extend(new_cols)
            query_assets = f"""
            SELECT
                es.source_id,
                es.source_name,
                es.source_type,
                es.subsector,
                ANY_VALUE(esl.location_geog) AS source_lat_lon,
                es.iso3_country,
                esl.gadm_0,
                esl.gadm_1,
                esl.gadm_2,
                EXTRACT(YEAR FROM es.start_time) AS year,
                COUNT(es.start_time) AS num_months,
                es.gas,
                SUM(es.emissions_quantity) AS emissions_quantity,
                es.emissions_factor_units,
                SUM(es.capacity) AS capacity,
                SUM(es.activity) AS activity,
                es.activity_units,
                CASE 
                    WHEN ST_DWithin(ANY_VALUE(esl.location_geog), {location_zone}, 0) THEN FALSE
                    WHEN ST_DWithin(ANY_VALUE(esl.location_geog), {buffer_zone_geom}, 0) THEN TRUE
                    ELSE FALSE
                END AS buffer,
                {new_cols_sql}
            FROM `trace-data-383422.climate_trace.emissions_sources` es
            LEFT JOIN `trace-data-383422.climate_trace.emissions_sources_location` esl
                ON es.source_id = esl.source_id
            WHERE
                es.gas = '{gas}'
                AND es.iso3_country = '{country}'
                AND es.start_time >= '{year}-01-01' AND es.start_time < '{year + 1}-01-01'
                AND es.subsector IN {sectors_str}
            GROUP BY
                es.source_id,
                es.source_name,
                es.source_type,
                es.subsector,
                es.iso3_country,
                esl.gadm_0,
                esl.gadm_1,
                esl.gadm_2,
                EXTRACT(YEAR FROM es.start_time),
                es.emissions_factor_units,
                es.activity_units,
                es.gas,
                {new_cols_sql}
            HAVING 
                (
                    ST_DWithin(ANY_VALUE(esl.location_geog), {location_zone}, 0)
                    OR (
                        ST_DWithin(ANY_VALUE(esl.location_geog), {buffer_zone_geom}, 0)
                        AND NOT ST_DWithin(ANY_VALUE(esl.location_geog), {location_zone}, 0)
                    )
                )
            ;
            """
        new_assets = run_bigquery(query_assets)

        if new_assets.empty:
            print("0 assets found")
        else:
            print("%s assets found" % len(new_assets))
            asset_sectors = new_assets["subsector"].unique()
            asset_sectors_str = "(" + ", ".join(f"'{s}'" for s in asset_sectors) + ")"

            gadm_0_expr = "ARRAY_TO_STRING(ARRAY_SLICE(SPLIT(ge.gadm_id, '.'), 0, 0), '.')"
            gadm_1_expr = "CONCAT(ARRAY_TO_STRING(ARRAY_SLICE(SPLIT(ge.gadm_id, '.'), 0, 1), '.'), '_1')"
            gadm_2_expr = "ARRAY_TO_STRING(ARRAY_SLICE(SPLIT(ge.gadm_id, '.'), 0, 2), '.')"
            query_gadm = f"""
            SELECT
                {gadm_0_expr} AS gadm_0,
                {gadm_1_expr} AS gadm_1,
                {gadm_2_expr} AS gadm_2,
                geom_0.name AS gadm_0_name,
                geom_1.name AS gadm_1_name,
                geom_2.name AS gadm_2_name,
                ge.subsector,
                ge.source_emissions,
                ge.source_activity
            FROM `trace-data-383422.climate_trace.gadm_emissions` ge
            LEFT JOIN `trace-data-383422.climate_trace.geometries` geom_0
                ON {gadm_0_expr} = REPLACE(geom_0.geometry_ref, 'gadm_', '')
            LEFT JOIN `trace-data-383422.climate_trace.geometries` geom_1
                ON {gadm_1_expr} = REPLACE(geom_1.geometry_ref, 'gadm_', '')
            LEFT JOIN `trace-data-383422.climate_trace.geometries` geom_2
                ON {gadm_2_expr} = REPLACE(geom_2.geometry_ref, 'gadm_', '')
            WHERE
                ge.gas = '{gas}'
                AND ge.iso3_country = '{country}'
                AND ge.start_time >= '{year}-01-01' AND ge.start_time < '{year + 1}-01-01'
                AND ge.subsector IN {asset_sectors_str}
            """
            gadm_combined_df = run_bigquery(query_gadm)

            if not gadm_combined_df.empty:
                for gadm_col_prefix in ["gadm_0", "gadm_1", "gadm_2"]:
                    gadm_name = gadm_col_prefix + "_name"
                    gadm_emissions = gadm_col_prefix + "_emissions_quantity"
                    gadm_activity = gadm_col_prefix + "_activity"
                    gadm_agg = gadm_combined_df.groupby(
                        [gadm_col_prefix, "subsector"], dropna=False
                    ).agg(
                        **{
                            gadm_name: (gadm_name, "first"),
                            gadm_emissions: ("source_emissions", "sum"),
                            gadm_activity: ("source_activity", "sum"),
                        }
                    ).reset_index()
                    new_assets = new_assets.merge(gadm_agg, how="left", on=[gadm_col_prefix, "subsector"])
            else:
                print(f"No GADM data found for {asset_sectors}, skipping merge.")
                for gadm_col_prefix in ["gadm_0", "gadm_1", "gadm_2"]:
                    for col in [gadm_col_prefix + "_name", gadm_col_prefix + "_activity", gadm_col_prefix + "_emissions_quantity"]:
                        new_assets[col] = pd.NA
            asset_df = pd.concat([asset_df, new_assets], ignore_index=True)

    if not asset_df.empty:
        asset_df["location"] = location
        asset_df["origin"] = origin
        asset_df["source_lat_lon"] = asset_df["source_lat_lon"].apply(wkt.loads)
        asset_df["source_km_from_origin"] = (
            asset_df.apply(
                lambda row: geodesic(
                    (row["origin"].y, row["origin"].x),
                    (row["source_lat_lon"].y, row["source_lat_lon"].x),
                ).meters,
                axis=1,
            )
            / 1000
        )
        asset_df["origin"] = asset_df["origin"].apply(lambda p: f"{p.y}, {p.x}")
        asset_df["source_lat_lon"] = asset_df["source_lat_lon"].apply(
            lambda p: f"{p.y}, {p.x}"
        )
        asset_df["emissions_factor"] = (
            asset_df["emissions_quantity"] / asset_df["activity"]
        )
        asset_df["gadm_0_emissions_factor"] = (
            asset_df["gadm_0_emissions_quantity"] / asset_df["gadm_0_activity"]
        )
        asset_df["gadm_1_emissions_factor"] = (
            asset_df["gadm_1_emissions_quantity"] / asset_df["gadm_1_activity"]
        )
        asset_df["gadm_2_emissions_factor"] = (
            asset_df["gadm_2_emissions_quantity"] / asset_df["gadm_2_activity"]
        )
        asset_df = asset_df[FINAL_COLS]

    return asset_df
