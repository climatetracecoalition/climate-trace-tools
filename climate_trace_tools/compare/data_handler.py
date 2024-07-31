import datetime
import json

import numpy as np
import pandas as pd
import psycopg2 as psycopg2
import importlib.resources as pkg_resources
from climate_trace_tools.data import supplementary
from climate_trace_tools.data import country
from io import BytesIO
import zipfile
from climate_trace_tools.data import source
import os


def get_ghg_gwps_list():
    with pkg_resources.open_text(supplementary, "ghgs.csv") as file:
        df = pd.read_csv(file)
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
    from climate_trace_tools.compare.subtract_out.util.constants import (
        DB_SOURCE_TO_COL_NAME,
    )

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


class CsvDataHandler:

    def read_csv_from_zip(self, module, inventory):
        # Open the ZIP file in binary mode
        with pkg_resources.open_binary(module, f"{inventory}.zip") as zip_binary_file:
            # Convert the binary file to a BytesIO object
            with zipfile.ZipFile(BytesIO(zip_binary_file.read())) as zip_file:
                # Open the CSV file inside the ZIP archive
                with zip_file.open(f"{inventory}.csv") as csv_file:
                    # Read the CSV file into a DataFrame
                    return pd.read_csv(csv_file)

    def load_all_data(self):
        all_data = pd.DataFrame()
        file_list = pkg_resources.contents(country)
        zip_files = [f for f in file_list if f.endswith(".zip")]
        for file in zip_files:
            inventory = file[:-4]
            data = self.read_csv_from_zip(country, inventory)
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

    def load_by_sector_country(self, inventory, iso3_country):

        df = self.read_csv_from_zip(country, inventory)
        # with pkg_resources.open_text(country, f"{inventory}.zip") as file:
        #     df = pd.read_csv(file)
        df["start_time"] = pd.to_datetime(df.start_time)
        df["end_time"] = pd.to_datetime(df.end_time)

        if iso3_country:
            df = df[df.iso3_country == iso3_country]

        return df
