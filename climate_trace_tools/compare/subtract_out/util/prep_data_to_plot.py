from climate_trace_tools.compare.subtract_out.util.constants import get_country_title
from climate_trace_tools.compare.subtract_out.util.country_lists import (
    countries_annex1,
    countries_nonannex1,
)
import pandas as pd
import numpy as np
import copy as copy
from climate_trace_tools.compare.subtract_out.util.generate_plots import plot
from climate_trace_tools.compare.subtract_out.util.logger_setup import logger


# def custom_groupby_sum(df, group_col, exclude_cols=None, min_count=1):
#     if exclude_cols is None:
#         exclude_cols = []
#
#     def agg_func(x):
#         if x.name in exclude_cols:
#             # For excluded columns, sum retaining NaNs
#             return np.nan if x.isna().any() else x.sum()
#         else:
#             # For non-excluded columns, sum ignoring NaNs
#             return x.sum(min_count=min_count)
#
#     # Group by and apply the custom aggregation
#     result = df.groupby(group_col, as_index=False).agg(agg_func)
#
#     return result


def custom_agg(df, exclude_cols=None, ff_cols=None, min_count=1):
    if exclude_cols is None:
        exclude_cols = []
    if ff_cols is None:
        ff_cols = []

    def agg_func(x):
        if x.name in ff_cols:
            # For forward-fill columns, use 'any' to preserve boolean values
            return x.any()
        elif x.name == "last_true_year":
            return x.max()
        elif x.name in exclude_cols:
            # For excluded columns, sum retaining NaNs
            return np.nan if x.isna().any() else x.sum()
        else:
            # For non-excluded columns, sum ignoring NaNs
            return x.sum(min_count=min_count)

    return agg_func


def combine_data(temp_dict, country):
    combo_df = pd.DataFrame()
    available = True
    missing_data = []
    sub_availabilities = []
    if len(temp_dict) == 0:
        available = False
    else:
        for key, item in temp_dict.items():
            # comparison_years = list(item.filter(regex="\d").columns)
            comparison_years = list(item.filter(regex=r"^\d+$").columns)
            ff_columns = list(item.filter(regex=r"^\d+_ff$").columns)
            COMP_COLS = [
                "Data source",
                "ID",
                "Sector",
                "Gas",
                "Unit",
                "last_true_year",
                "carbon_eq",
            ] + comparison_years

            df = item[item.ID == f"{country}"].reset_index(drop=True)
            available = True
            if df.empty:
                available = False
            sub_availabilities.append(available)
            if df.empty:
                logger.debug(
                    f"No data available for {key.upper()} in {country.upper()}"
                )
                missing_data.append(key)  # document which sectors are not available
                continue

            df["carbon_eq"] = "none"
            # df = df[COMP_COLS]

            hundred_yr = copy.deepcopy(df)
            # hundred_cols = hundred_yr.filter(regex="\d").columns
            hundred_cols = hundred_yr.filter(regex=r"^\d+$").columns
            hundred_yr.loc[hundred_yr["Gas"] == "ch4", hundred_cols] = (
                hundred_yr.loc[hundred_yr["Gas"] == "ch4", hundred_cols] * 28
            )
            hundred_yr.loc[hundred_yr["Gas"] == "n2o", hundred_cols] = (
                hundred_yr.loc[hundred_yr["Gas"] == "n2o", hundred_cols] * 265
            )
            hundred_yr["carbon_eq"] = "100-year"

            twenty_yr = copy.deepcopy(df)
            # twenty_cols = twenty_yr.filter(regex="\d").columns
            twenty_cols = twenty_yr.filter(regex=r"^\d+$").columns

            twenty_yr.loc[twenty_yr["Gas"] == "ch4", twenty_cols] = (
                twenty_yr.loc[twenty_yr["Gas"] == "ch4", twenty_cols] * 84
            )
            twenty_yr.loc[twenty_yr["Gas"] == "n2o", twenty_cols] = (
                twenty_yr.loc[twenty_yr["Gas"] == "n2o", twenty_cols] * 264
            )
            twenty_yr["carbon_eq"] = "20-year"

            combo_df = pd.concat([combo_df, df, hundred_yr, twenty_yr])

        if not combo_df.empty:
            # try to figure out if a certain inventory has all NULLs for a certain year
            numeric_cols = combo_df.filter(regex=r"^\d+$").columns
            ff_cols = combo_df.filter(regex=r"^\d+_ff$").columns
            check_nans = combo_df.groupby("Data source")[numeric_cols].sum(min_count=1)
            columns_with_nans = check_nans.columns[check_nans.isna().any()].tolist()

            agg_func = custom_agg(
                combo_df, exclude_cols=columns_with_nans, ff_cols=ff_cols
            )
            totals_df = combo_df.groupby(["Gas", "carbon_eq"], as_index=False).agg(
                agg_func
            )

            totals_df["Sector"] = "Subtotal"
            totals_df["ID"] = country
            totals_df["Unit"] = "tonnes"
            totals_df["Data source"] = "gapfilled"
            totals_df = totals_df[COMP_COLS]
            grand_totals = totals_df.groupby("carbon_eq", as_index=False).agg(agg_func)

            grand_totals["Gas"] = "co2e"
            grand_totals["Sector"] = "Total"
            grand_totals["ID"] = country
            grand_totals["Unit"] = "tonnes"
            grand_totals["Data source"] = "gapfilled"
            grand_totals = grand_totals[COMP_COLS]

            subsector_df = combo_df.groupby(
                ["Sector", "carbon_eq", "Data source"], as_index=False
            ).agg(agg_func)

            subsector_df["Gas"] = "co2e"
            subsector_df["ID"] = country
            subsector_df["Unit"] = "tonnes"
            subsector_df = subsector_df[COMP_COLS]

            combo_df = pd.concat([combo_df, totals_df, subsector_df, grand_totals])
            combo_df[ff_cols] = combo_df[ff_cols].ffill(axis=0)

    return combo_df, sub_availabilities, missing_data


def compare(comparison_dict, country, allinv, sector, ratio_data):
    """Create the plotting dictionary with data combined according to comparison dictionaries and ready to plot"""
    logger.info(f"Attempting comparison for {sector} in {country}")
    plotting_dict = {}
    for compare_inventory, subinvdict in comparison_dict.items():
        logger.debug(
            f"Calculating comparison to {compare_inventory.upper()} {sector} {country}"
        )
        temp_dict = {}
        availabilities = []
        for subinv, termdetails in subinvdict.items():
            logger.debug(f"Manipulating data from {subinv.upper()}")
            for tup in termdetails:
                df = allinv[
                    (allinv.Sector == f"{tup[0]}")
                    & (allinv["Data source"] == f"{subinv}")
                ].copy()
                if not df.empty:
                    # data_cols = df.filter(regex="\d").columns
                    # Separate year columns and 'is_ff' columns
                    year_cols = [
                        col
                        for col in df.columns
                        if isinstance(col, (int, str)) and str(col).isdigit()
                    ]
                    ff_cols = [
                        col
                        for col in df.columns
                        if isinstance(col, str) and col.endswith("_ff")
                    ]

                    # Multiply only the year columns
                    df.loc[:, year_cols] = df.loc[:, year_cols] * tup[1]

                    data_cols = year_cols + ff_cols
                    temp_dict[f"{tup[0]}"] = df[
                        df.columns.drop(data_cols).tolist() + data_cols
                    ]
                    # temp_dict[f"{tup[0]}"] = df
                if (
                    df.empty
                ):  # store empty ef so that we can record missing data in combine_data func
                    temp_dict[f"{tup[0]}"] = df
            combo_df, sub_availabilities, missing_data = combine_data(
                temp_dict, country
            )

            availabilities.extend(
                sub_availabilities
            )  # sub_availabilities tracks availabilit of all subitems within one subinv

        plotting_dict[compare_inventory] = combo_df

        # if there is no climate-trace data for this sector/country, don't retunr anything
        # Check if climate-trace data exists for this sector/country
        if "climate-trace" not in plotting_dict or plotting_dict["climate-trace"].empty:
            logger.debug(f"No Climate TRACE data available for {sector} in {country}")
            return plotting_dict, pd.DataFrame()

        if sum(availabilities) >= 1:
            ratio_agg = combo_df.loc[
                (combo_df["carbon_eq"] == "100-year")
                & ((combo_df["Sector"] == "Subtotal") | (combo_df["Sector"] == "Total"))
            ].copy()
            ratio_agg["Data source"] = compare_inventory
            ratio_agg["Sector"] = sector
        if sum(availabilities) == len(
            availabilities
        ):  # indicates all data was available for comparison
            ratio_agg["data_available"] = "complete"
        elif sum(availabilities) == 0:
            continue
        elif sum(availabilities) < len(
            availabilities
        ):  # indicates some inventories missing from comparison
            ratio_agg["data_available"] = "missing " + ", ".join(
                [item for item in missing_data]
            )
        ratio_data = pd.concat([ratio_data, ratio_agg])
    return plotting_dict, ratio_data


def create_plots(
    allinv,
    countries,
    sector,
    gas,
    co2eq,
    plot_type,
    ratio_data,
    output_folder,
    comparison_dicts,
    title_dicts,
    create_folders,
    plot_live,
):

    for country in countries:
        if country is np.nan:
            continue
        if country in countries_annex1:
            master_comparison_dict = comparison_dicts["annex1"]
            title_dict = title_dicts["annex1"]
        elif country in countries_nonannex1:
            master_comparison_dict = comparison_dicts["nonannex1"]
            title_dict = title_dicts["nonannex1"]
        else:
            master_comparison_dict = comparison_dicts["nonannex1"]

        try:
            comparison_dict = master_comparison_dict[sector]
        except KeyError:
            print(f"Calculated comparison not available for {sector} in {country}")
            continue

        plotting_dict, ratio_data = compare(
            comparison_dict, country, allinv, sector, ratio_data
        )

        if "climate-trace" not in plotting_dict or plotting_dict["climate-trace"].empty:
            logger.info(
                f"Skipping plot for {sector} in {country} due to missing Climate TRACE data"
            )
            continue

        if not all(plotting_dict[d].empty for d in plotting_dict.keys()):
            try:
                plot(
                    sector,
                    country,
                    gas,
                    co2eq,
                    plot_type,
                    title_dict,
                    output_folder,
                    plotting_dict,
                    create_folders,
                    plot_live,
                )
            except AttributeError:
                logger.error(f"Attribute missing for {sector} in {country} plot")
                continue
        else:
            logger.debug(f"No data to plot for {sector} in {country}")

    return ratio_data
