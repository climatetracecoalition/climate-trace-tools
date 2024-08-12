from climate_trace_tools.compare.subtract_out.util.constants import get_country_title
from climate_trace_tools.compare.subtract_out.util.country_lists import (
    countries_annex1,
    countries_nonannex1,
)
import pandas as pd
import numpy as np
import copy as copy
from climate_trace_tools.compare.subtract_out.util.generate_plots import plot


def nan_sum_with_min_count(series, min_count=1):
    if series.count() < min_count:
        return np.nan
    return np.nan if series.isna().any() else series.sum()


def custom_groupby_sum(df, group_col, exclude_cols=None):
    if exclude_cols is None:
        exclude_cols = []

    def agg_func(x):
        if x.name in exclude_cols:
            return x.sum()
        else:
            return np.nan if x.isna().any() else x.sum()

    # Group by and apply the custom aggregation
    result = df.groupby(group_col, as_index=False).agg(agg_func)

    return result


def custom_groupby_sum(df, group_col, exclude_cols=None, min_count=1):
    if exclude_cols is None:
        exclude_cols = []

    def agg_func(x):
        if x.name in exclude_cols:
            # For excluded columns, sum retaining NaNs
            return np.nan if x.isna().any() else x.sum()
        else:
            # For non-excluded columns, sum ignoring NaNs
            return x.sum(min_count=min_count)

    # Group by and apply the custom aggregation
    result = df.groupby(group_col, as_index=False).agg(agg_func)

    return result


def combine_data(temp_dict, country):
    combo_df = pd.DataFrame()
    available = True
    missing_data = []
    sub_availabilities = []
    if len(temp_dict) == 0:
        available = False
    else:
        for key, item in temp_dict.items():
            comparison_years = list(item.filter(regex="\d").columns)
            COMP_COLS = [
                "Data source",
                "ID",
                "Sector",
                "Gas",
                "Unit",
                "carbon_eq",
            ] + comparison_years

            df = item[item.ID == f"{country}"].reset_index(drop=True)
            available = True
            if df.empty:
                available = False
            sub_availabilities.append(available)
            if df.empty:
                print(f"No data available for {key.upper()} in {country.upper()}")
                missing_data.append(key)  # document which sectors are not available
                continue

            df["carbon_eq"] = "none"
            # df = df[COMP_COLS]

            hundred_yr = copy.deepcopy(df)
            hundred_cols = hundred_yr.filter(regex="\d").columns
            hundred_yr.loc[hundred_yr["Gas"] == "ch4", hundred_cols] = (
                hundred_yr.loc[hundred_yr["Gas"] == "ch4", hundred_cols] * 28
            )
            hundred_yr.loc[hundred_yr["Gas"] == "n2o", hundred_cols] = (
                hundred_yr.loc[hundred_yr["Gas"] == "n2o", hundred_cols] * 265
            )
            hundred_yr["carbon_eq"] = "100-year"

            twenty_yr = copy.deepcopy(df)
            twenty_cols = twenty_yr.filter(regex="\d").columns
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
            check_nans = combo_df.groupby("Data source")[hundred_cols].sum(min_count=1)
            columns_with_nans = check_nans.columns[check_nans.isna().any()].tolist()
            totals_df = custom_groupby_sum(
                combo_df,
                group_col=["Gas", "carbon_eq"],
                exclude_cols=columns_with_nans,
                min_count=1,
            )
            # totals_df = combo_df.groupby(["Gas", "carbon_eq"], as_index=False).agg(
            #     lambda x: nan_sum_with_min_count(x, min_count=0)
            # )

            totals_df["Sector"] = "Subtotal"
            totals_df["ID"] = country
            totals_df["Unit"] = "tonnes"
            totals_df["Data source"] = "gapfilled"
            totals_df = totals_df[COMP_COLS]

            grand_totals = custom_groupby_sum(
                totals_df,
                group_col="carbon_eq",
                exclude_cols=columns_with_nans,
                min_count=1,
            )
            # grand_totals = totals_df.groupby("carbon_eq", as_index=False).sum()
            grand_totals["Gas"] = "co2e"
            grand_totals["Sector"] = "Total"
            grand_totals["ID"] = country
            grand_totals["Unit"] = "tonnes"
            grand_totals["Data source"] = "gapfilled"
            grand_totals = grand_totals[COMP_COLS]

            subsector_df = custom_groupby_sum(
                combo_df,
                group_col=["Sector", "carbon_eq", "Data source"],
                exclude_cols=columns_with_nans,
                min_count=1,
            )
            # subsector_df = combo_df.groupby(
            #     ["Sector", "carbon_eq", "Data source"], as_index=False
            # ).sum()
            subsector_df["Gas"] = "co2e"
            subsector_df["ID"] = country
            subsector_df["Unit"] = "tonnes"
            subsector_df = subsector_df[COMP_COLS]

            combo_df = pd.concat([combo_df, totals_df, subsector_df, grand_totals])

    return combo_df, sub_availabilities, missing_data


def compare(comparison_dict, country, allinv, sector, ratio_data):
    """Create the plotting dictionary with data combined according to comparison dictionaries and ready to plot"""

    plotting_dict = {}
    for compare_inventory, subinvdict in comparison_dict.items():
        print(
            f"Calculating comparison to {compare_inventory.upper()} {sector} {country}"
        )
        temp_dict = {}
        availabilities = []
        for subinv, termdetails in subinvdict.items():
            print(f"       Manipulating data from {subinv.upper()}")
            for tup in termdetails:
                df = allinv[
                    (allinv.Sector == f"{tup[0]}")
                    & (allinv["Data source"] == f"{subinv}")
                ].copy()
                if not df.empty:
                    data_cols = df.filter(regex="\d").columns
                    df.loc[:, data_cols] = df.loc[:, data_cols] * tup[1]
                    temp_dict[f"{tup[0]}"] = df
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

        if not (
            all(plotting_dict[d].empty for d in plotting_dict.keys())
            or plotting_dict["climate-trace"].empty
        ):
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
                print(f"Attribute missing for {sector} in {country} plot")
                continue
        else:
            print(f"No data to plot for {sector} in {country}")

    return ratio_data
