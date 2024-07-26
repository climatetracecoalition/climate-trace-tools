import datetime
import json

import numpy as np
import pandas as pd
import psycopg2 as psycopg2
import os
from compare.subtract_out.util.constants import DB_SOURCE_TO_COL_NAME

# from db_connect.dh_utils import parse_and_format_query_data, parse_format_asset


def get_ghg_gwps_list():
    df = pd.read_csv("../../data/supplementary/ghgs.csv")
    df = df[["lower_designation", "gwp_20yr", "gwp_100yr"]]
    return df


def calculate_gwp(datasourcedf):
    """
    Function calculates 100 and 20 yr GWPs for any dataset matching CT format,
    where the GWPs are missing from gases, and returns updated data frame.
    """
    cols = [
        "iso3_country",
        "reporting_entity",
        "start_time",
        "end_time",
        "original_inventory_sector",
    ]

    gases = datasourcedf["gas"].unique()
    gases = [gas for gas in gases if gas not in ["co2e_100yr", "co2e_20yr"]]
    datasourcedf = datasourcedf.fillna(0)
    df_pivot = pd.pivot_table(
        data=datasourcedf,
        values="emissions_quantity",
        index=cols,
        columns="gas",
        dropna=True,
    ).reset_index()

    gas_df = get_ghg_gwps_list()

    df_pivot["co2e_20yr"] = 0
    df_pivot["co2e_100yr"] = 0

    ignore_cols = cols + ["co2e_100yr", "co2e_20yr"]
    gases = [column for column in df_pivot.columns if column not in ignore_cols]
    df_pivot[gases] = df_pivot[gases].fillna(0)
    for gas in gases:
        gas_info = gas_df[gas_df["lower_designation"] == gas]
        gwp_20yr = gas_info["gwp_20yr"].values[0]
        gwp_100yr = gas_info["gwp_100yr"].values[0]
        df_pivot["co2e_20yr"] += gwp_20yr * df_pivot[gas]
        df_pivot["co2e_100yr"] += gwp_100yr * df_pivot[gas]

    df_pivot_melt = df_pivot.melt(
        id_vars=cols, var_name="gas", value_name="emissions_quantity"
    )

    df_pivot_melt["sector_id"] = "None"
    df_pivot_melt["emissions_quantity_units"] = "tonnes"
    df_pivot_melt["temporal_granularity"] = "annual"
    df_pivot_melt["created_date"] = "None"
    df_pivot_melt["modified_date"] = "None"

    return df_pivot_melt


def parse_and_format_query_data(
    df, years_to_columns=True, rename_columns=True, times_to_years=True
):

    if times_to_years:
        df["start_time"] = pd.to_datetime(df.start_time)
        df["year"] = df.start_time.dt.year
        df.rename(columns={"start_time": "year"})

    df = df.groupby(
        [
            "original_inventory_sector",
            "iso3_country",
            "reporting_entity",
            "gas",
            "emissions_quantity_units",
            "year",
        ],
        as_index=False,
    ).sum()

    if rename_columns:
        df = df.rename(columns=DB_SOURCE_TO_COL_NAME)

    if years_to_columns:
        transformed_df = df.pivot(
            index=["Sector", "ID", "Data source", "Gas", "Unit"],
            columns="year",
            values="emissions_quantity",
        ).reset_index()

        # missing_years = [cy for cy in COMP_YEARS if cy not in transformed_df.columns]

        # transformed_df = transformed_df.reindex(columns=transformed_df.columns.tolist() + missing_years)
        transformed_df = transformed_df.reindex(columns=transformed_df.columns.tolist())

    return transformed_df


def load_data():
    all_data = pd.DataFrame()

    for file in os.listdir("../../data/country"):
        if file.startswith(".DS"):
            continue
        data = pd.read_csv(f"../../data/country/{file}")
        all_data = pd.concat([all_data, data])

    all_data = all_data[
        [
            "original_inventory_sector",
            "iso3_country",
            "reporting_entity",
            "gas",
            "emissions_quantity",
            "emissions_quantity_units",
            "start_time",
            "end_time",
        ]
    ]

    all_data = all_data[all_data.gas.isin(["co2", "n2o", "ch4"])]

    # all_data = calculate_gwp(all_data)
    all_data = all_data.drop(columns="end_time")

    transformed_data = parse_and_format_query_data(all_data)

    return transformed_data


# def init_db_connect():
#
#     pghost = os.getenv("CLIMATETRACE_HOST", "127.0.0.1")
#     pguser = os.getenv("CLIMATETRACE_USER", "chromacloud")
#     pgpass = os.getenv("CLIMATETRACE_PASS")
#     pgport = os.getenv("CLIMATETRACE_PORT", "5432")
#     pgdb = os.getenv("CLIMATETRACE_DB")
#     con_str = f"host='{pghost}' dbname='{pgdb}' user='{pguser}' password='{pgpass}' port='{pgport}'"
#     conn = psycopg2.connect(con_str)
#
#     return conn
#
#
# class DataHandler:
#     def __init__(self):
#         self.conn = init_db_connect()
#
#     # def get_params(self):
#     #     with open(self.params_file, 'r') as fid:
#     #         params = json.load(fid)
#     #     return params
#
#     def get_cursor(self):
#         if not self.conn:
#             raise ConnectionError("No database connection has been established!")
#         if self.conn.closed:
#             raise ConnectionError("The database connection is closed!")
#
#         return self.conn.cursor()
#
#     def load_data(self, years_to_columns=False, rename_columns=True,
#                   start_date=datetime.date(1990, 1, 1)):
#         curs = self.get_cursor()
#
#         curs.execute("SELECT original_inventory_sector, iso3_country, reporting_entity, "
#                          "gas, emissions_quantity, emissions_quantity_units, start_time "
#                          "FROM country_emissions_staging WHERE start_time >= %s "
#                          "AND (gas = 'co2' OR gas = 'n2o' OR gas = 'ch4') "
#                          "AND reporting_entity != 'climate-trace'"
#                          "AND iso3_country <> ''",
#                          (start_date,))
#
#         colnames = [desc[0] for desc in curs.description]
#         data = pd.DataFrame(data = np.array(curs.fetchall()), columns=colnames)
#         allinv = parse_and_format_query_data(data,years_to_columns=years_to_columns, rename_columns=rename_columns)
#         return allinv
#
#     def load_province_data(self, years_to_columns=True, rename_columns=False, province=True):
#         curs = self.get_cursor()
#
#         curs.execute("SELECT region_code, iso3_country, start_time, original_inventory_sector, asset_name, "
#                      "gas, emissions_quantity, location "
#                      "FROM province_emissions "
#                      "WHERE original_inventory_sector NOT IN ('net-forest-emissions', 'net-grassland-emissions', 'net-wetland-emissions')")
#
#         colnames = [desc[0] for desc in curs.description]
#         return parse_and_format_query_data(pd.DataFrame(data=np.array(curs.fetchall()), columns=np.array(colnames)),
#                                            years_to_columns=years_to_columns, rename_columns=rename_columns, province=province)
#
#     def load_assets(self, asset_names, start_date=datetime.date(2015, 1, 1)):
#         curs = self.get_cursor()
#
#         curs.execute("SELECT iso3_country, original_inventory_sector, start_time, asset_id, gas, emissions_quantity "
#                      "FROM asset_emissions "
#                      "WHERE gas <> 'co2e_20yr' AND original_inventory_sector = 'synthetic-fertilizer-application' ", # IN ('aluminum', 'bauxite-mining', 'cement', 'coal-mining', 'copper-mining', 'domestic-aviation', 'electricity-generation', 'enteric-fermentation', 'international-aviation', 'iron-mining', 'manure-management', 'oil-and-gas-production-and-transport', 'oil-and-gas-refining', 'road-transportation', 'shipping', 'solid-waste-disposal', 'steel', 'pulp-and-paper') ",
#                          (start_date,))
#
#         colnames = [desc[0] for desc in curs.description]
#         return parse_format_asset(pd.DataFrame(data=np.array(curs.fetchall()), columns=np.array(colnames)), asset_names, country=False)
#
#     def load_country_totals(self, asset_names, start_date=datetime.date(2015, 1, 1)):
#         curs = self.get_cursor()
#
#         curs.execute("SELECT iso3_country, original_inventory_sector, start_time, gas, emissions_quantity "
#                          "FROM country_emissions WHERE reporting_entity = 'climate-trace' "
#                      "AND gas <> 'co2e_20yr' AND original_inventory_sector = 'synthetic-fertilizer-application' ", #('aluminum', 'bauxite-mining', 'biological-treatment-of-solid-waste-&-biogenic', 'cement', 'chemicals', 'coal-mining', 'copper-mining', 'cropland-fires', 'domestic-aviation', 'electricity-generation', 'enteric-fermentation', 'fluorinated-gases', 'incineration-and-open-burning-of-waste', 'international-aviation', 'iron-mining', 'manure-management', 'net-forest-emissions', 'net-grassland-emissions', 'net-wetland-emissions', 'oil-and-gas-production-and-transport', 'oil-and-gas-refining', 'other-agricultural-soil-emissions', 'other-energy-use', 'other-fossil-fuel-operations', 'other-manufacturing', 'other-onsite-fuel-usage', 'other-transport', 'pulp-and-paper', 'railways', 'residential-and-commercial-onsite-fuel-usage', 'rice-cultivation', 'road-transportation', 'rock-quarrying', 'sand-quarrying', 'shipping', 'solid-fuel-transformation', 'solid-waste-disposal', 'steel', 'synthetic-fertilizer-application', 'wastewater-treatment-and-discharge') ",
#                          (start_date,))
#
#         colnames = [desc[0] for desc in curs.description]
#         return parse_format_asset(pd.DataFrame(data=np.array(curs.fetchall()), columns=np.array(colnames)), asset_names, country=True)
#
#     def get_asset_names(self):
#
#         query = f"SELECT asset_id, asset_name " \
#                 f"FROM asset_information " \
#                 f"WHERE original_inventory_sector = 'synthetic-fertilizer-application' "# ('aluminum', 'bauxite-mining', 'cement', 'coal-mining', 'copper-mining', 'domestic-aviation', 'electricity-generation', 'enteric-fermentation', 'international-aviation', 'iron-mining', 'manure-management', 'oil-and-gas-production-and-transport', 'oil-and-gas-refining', 'road-transportation', 'shipping', 'solid-waste-disposal', 'steel') "
#
#         with self.conn.cursor() as cur:
#             cur.execute(query)
#             res = cur.fetchall()
#             name_id_map = {}
#
#             for r in res:
#                 key = r[0]
#                 name_id_map[key] = r[1]
#         return name_id_map
#
#     def get_asset_types(self):
#
#         query = f"SELECT asset_id, asset_type " \
#                 f"FROM asset_information " \
#                 f"WHERE original_inventory_sector = 'synthetic-fertilizer-application' "# IN ('aluminum', 'bauxite-mining', 'cement', 'coal-mining', 'copper-mining', 'domestic-aviation', 'electricity-generation', 'enteric-fermentation', 'international-aviation', 'iron-mining', 'manure-management', 'oil-and-gas-production-and-transport', 'oil-and-gas-refining', 'road-transportation', 'shipping', 'solid-waste-disposal', 'steel') "
#
#         with self.conn.cursor() as cur:
#             cur.execute(query)
#             res = cur.fetchall()
#             name_id_map = {}
#
#             for r in res:
#                 key = r[0]
#                 name_id_map[key] = r[1]
#         return name_id_map
#
#     def fertilizer_look_up(self):
#         with self.conn.cursor() as curs:
#             curs.execute("CREATE OR REPLACE FUNCTION agg_loop() "
#                          "RETURNS void AS $$ "
#                          "DECLARE "
#                          "  i INTEGER; "
#                          "  asset_array VARCHAR(100); "
#                          "BEGIN "
#                          "  FOR i IN (SELECT uid FROM fertilizer_activity_lookup) "
#                          "      LOOP "
#                          "          SELECT asset_id into asset_array "
#                          "          FROM asset_information "
#                          "          WHERE original_inventory_sector = 'synthetic-fertilizer-application' "
#                          "          AND CAST(iso3_country AS CHAR(3)) = CAST(( "
#                          "              SELECT iso3_country "
#                          "              FROM fertilizer_activity_lookup "
#                          "              WHERE uid = i) AS CHAR(3)) "
#                          "          AND asset_type = ( "
#                          "              SELECT crop_type "
#                          "              FROM fertilizer_activity_lookup "
#                          "              WHERE uid = i); "
#                          "          UPDATE asset_emissions "
#                          "          SET activity = ( "
#                          "              SELECT activity"
#                          "              FROM fertilizer_activity_lookup "
#                          "              WHERE uid = i) "
#                          "          WHERE start_time = ( "
#                          "              SELECT start_date "
#                          "              FROM fertilizer_activity_lookup "
#                          "              WHERE uid = i) "
#                          "          AND CAST(asset_id AS bigint) IN (CAST(asset_array AS bigint)); "
#                          "          RAISE NOTICE 'Parsing Row %', i; "
#                          "      END LOOP; "
#                          "END; "
#                          "$$ "
#                          "LANGUAGE plpgsql; "
#                          "SELECT agg_loop();")
#
