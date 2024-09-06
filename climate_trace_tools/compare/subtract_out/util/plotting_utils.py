import pandas as pd
from climate_trace_tools.compare.subtract_out.util.constants import (
    get_gas_title,
    get_country_title,
)
from climate_trace_tools.compare.subtract_out.util.country_lists import (
    countries_annex1,
    countries_nonannex1,
)
import numpy as np
import json
import importlib.resources as pkg_resources
from climate_trace_tools.compare.subtract_out.util.logger_setup import logger
from climate_trace_tools.compare.subtract_out import files

# Settings for which data to plot

# GASES: 'all' to plot co2e for total co2, ch4, and n2o
## or specify 'co2', 'ch4', and 'n2o' for plots with only that gas

# CO2EQ: choose: '100-year', '20-year', 'both', or 'none'
## 'none' is available for plots showing one gas, this option is skipped when 'all' is specified for GASES
## CO2EQ defaults to 'none' for plots showing only 'co2', while ch4 and n2o can take any setting
## 'both' shows comparison between 100-year and 20-year estimates on a single plot

# PLOT_TYPE: 'subsectors' shows breakdown by subsector, it is available for every gas and co2eq setting
## PLOT_TYPE 'gases' shows a breakdown by each gas's contribution to the total for a sector. It is available for 'all' gases only.
## 'gases' setting requires CO2EQ not be 'none'

# start_year and end_year are the year range for the plot Note: this only selects which years to plot from the dataset
# downloaded from the SQL database. The SQL database has its own year range setting of 1990-2022. For earlier years,
# you need to also change the COMP_YEARS variable in db_connect.constants

# countries: Can pick countries_annex1, countries_nonannex1, or use top30_dict, or make your own
## custom list of countries. You can make new country lists in comparisons.dictionaries.country_lists
## top30_dict contains lists of countries for each sector that were the top emitters according to Climate TRACE in 2020

# sectors_to_plot: Can pick master_dict_annex1.keys(), master_dict_nonannex1.keys(), or your own
## list of sectors. Keep in mind, only sectors named in those dictionaries can be specified in custom list.
## For instance 'aviation' is a plotting sector, 'international-aviation' and 'domestic-aviation' are not.

with pkg_resources.open_text(files, "master_comparison_dict_annex1.json") as file_path:
    master_dict_annex1 = json.load(file_path)

ratio_sectors = []


for item in master_dict_annex1.keys():
    invs = master_dict_annex1[item].keys()
    if not all([inv == "climate-trace" for inv in invs]) and any(
        [inv == "climate-trace" for inv in invs]
    ):
        ratio_sectors.append(item)


countries = countries_annex1 + countries_nonannex1


# Dict containing the year after the last year that an inventory reported data
missing_years = {
    "unfccc_annex_1": 2021,
    "unfccc_non_annex_1": 2020,
    "pik-tp": 2020,
    "pik-cr": 2020,
    #'edgar': 2019,
    "cait": 2019,
    "faostat": 2020,
}

# Settings for basic aesthetic characters for all plots

# Line/point color for data sources
color_dictionary = {
    "climate-trace": "mediumseagreen",
    "unfccc_annex_1": "chocolate",
    "unfccc_non_annex_1": "chocolate",
    "pik-tp": "blueviolet",
    "edgar": "deepskyblue",
    "cait": "deeppink",
    "ceds": "orange",
    "carbon-monitor": "red",
    "faostat": "gold",
    "iea": "yellow",
    "gosat": "red",
}

# Line style settings for gases plots
gas_lines = {"co2": "longdashdot", "ch4": "dash", "n2o": "dot", "co2e": "solid"}


# plot layout
def get_layout(country, title_dict, sector):
    layout = {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "title": f"Comparing emissions estimates from ClimateTRACE vs. other inventories"
        + f"<br><span style='font-size: 20px;'>{title_dict[sector]['title']} in "
        f"{get_country_title(country)}</span><br><br><br><br>",
        "title_font": {"size": 25},
        "title_y": 0.95,
        "legend": {
            "traceorder": "normal",
            "groupclick": "toggleitem",
            "x": 1.05,
        },
        "margin": {"l": 100, "r": 400, "t": 140, "b": 80},
    }
    return layout


fonts = {"family": "Foros, medium", "color": "darkblue"}


# y axis
def get_yaxes(gas, co2eq):
    if gas == "all" and co2eq != "both":
        title = f"Tons  CO<sub>2</sub>e  {co2eq}  GWP"
    elif co2eq != "none" and co2eq != "both" and gas != "all":
        title = f"Tons  {get_gas_title(gas)}  CO<sub>2</sub>e  {co2eq}  GWP"
    elif co2eq == "both":
        title = f"Tons CO<sub>2</sub>e"
    else:
        title = f"Tons  {get_gas_title(gas)}"

    yaxes = {
        "gridcolor": "#e6f3ff",
        "linewidth": 1,
        "ticks": "outside",
        "tickcolor": "#e6f3ff",
        "tickwidth": 1,
        "ticklen": 20,
        "zeroline": True,
        "zerolinewidth": 1,
        "zerolinecolor": "#e6f3ff",
        "showline": True,
        "linecolor": "#e6f3ff",
        "title": title,
    }
    return yaxes


# x axis
xaxes = {"gridcolor": "#e6f3ff", "linewidth": 1}

# Sets position of each inventory in the plot
legend_rank = {
    "climate-trace": 1,
    "unfccc_annex_1": 2,
    "unfccc_non_annex_1": 2,
    "pik-tp": 2,
    "edgar": 2,
    "cait": 2,
    "ceds": 2,
    "carbon-monitor": 2,
    "faostat": 2,
    "iea": 2,
    "gosat": 2,
}

# Determines whether plot defaults to a data source being visible
visibility = {
    "climate-trace": True,
    "unfccc_annex_1": "legendonly",
    "unfccc_non_annex_1": "legendonly",
    "pik-tp": "legendonly",
    "edgar": "legendonly",
    "ceds": "legendonly",
    "cait": "legendonly",
    "carbon-monitor": "legendonly",
    "faostat": "legendonly",
    "iea": "legendonly",
    "gosat": "legendonly",
}

# Titles for total calculated comparison traces by data source
total_title = {
    "climate-trace": "Total estimate from ClimateTRACE",
    "unfccc_annex_1": "Total comparable estimate from UNFCCC",
    "unfccc_non_annex_1": "Total comparable estimate from UNFCCC",
    "pik-tp": "Total comparable estimate from PIK",
    "edgar": "Total comparable estimate from EDGAR",
    "ceds": "Total compareable estimate from CEDS",
    "cait": "Total comparable estimate from CAIT",
    "carbon-monitor": "Total comparable estimate from Carbon Monitor",
    "faostat": "Total comparable estimate from FAO",
    "iea": "Total comparable estimate from IEA",
    "gosat": "Total comparable estimate from GOSAT",
}

# How to Use this Graph annotation
annotation = {
    "text": "How to Use this Graph",
    "showarrow": False,
    "align": "left",
    "xref": "paper",
    "yref": "paper",
    "x": -0.004,
    "y": 1.05,
    "hovertext": "TBD",
}

# Only for 'both' co2eq plots, determines whether 100 or 20 year has markers
line_dictionary = {"100-year": "lines", "20-year": "lines+markers", "none": "lines"}


# Set point symbol for cases in co2eq 'both' plots where data points are missing
def get_point_symbol(co2eq, gwp):
    if co2eq == "both" and gwp == "20-year":
        point_symbol = "cross"
    else:
        point_symbol = "diamond"
    return point_symbol


gwp_list = {
    "both": ["100-year", "20-year"],
    "100-year": ["100-year"],
    "20-year": ["20-year"],
    "none": ["none"],
}

formulas = ["co2", "ch4", "n2o"]


def get_legend_title_params(
    title_dict, comparison_years, sector, key, data_present, nonzero_emissions
):
    startyear = comparison_years[0]
    endyear = comparison_years[-1]

    basic_title = f'<br><br><span style="font-size: 16px;">{title_dict[sector]["legend"][key][key]["desc"]}</span>'
    if data_present and nonzero_emissions:
        legend_name = basic_title
    elif not data_present:
        legend_name = basic_title + f'<span style="font-size: 12px;">  No Data</span>'
    elif not nonzero_emissions:
        legend_name = (
            basic_title + f'<span style="font-size: 12px;">  estimate is zero</span>'
        )

    legend_title_params = {
        "x": [startyear],
        "y": [0],
        "name": legend_name,
        "legendgroup": key,
        "legendrank": legend_rank[key],
        "mode": "lines",
        "line": {"color": "rgba(0,0,0,0)"},
    }

    return legend_title_params


def is_data_present(item, key):
    data_present = True
    nonzero_emissions = True

    if item.empty is True:
        data_present = False
    else:
        baseline_present = item["Data source"].str.find(key)

        if not any(
            [baseline_present.iloc[i] > -1 for i in list(range(len(baseline_present)))]
        ):
            data_present = False
        else:
            data_years = item.filter(regex="\d").columns
            if item.loc[item["Data source"] == key, data_years].sum().sum() == 0:
                nonzero_emissions = False

    return data_present, nonzero_emissions


def is_gas_present(key, item):
    gas_presence = {
        "co2": {"data_present": True, "nonzero_emissions": True},
        "ch4": {"data_present": True, "nonzero_emissions": True},
        "n2o": {"data_present": True, "nonzero_emissions": True},
    }
    for formula in formulas:
        if item.empty:
            gas_presence[formula]["data_present"] = False
        else:
            data_years = item.filter(regex="\d").columns
            formula_present = item.loc[item["Gas"] == formula, data_years]
            if all(
                [
                    formula_present[column].isnull().all()
                    for column in formula_present.columns
                ]
            ):
                gas_presence[formula]["data_present"] = False
            elif item.loc[item["Gas"] == formula, data_years].sum().sum() == 0:
                gas_presence[formula]["nonzero_emissions"] = False
            else:
                gas_presence[formula]["data_present"] = True
                gas_presence[formula]["nonzero_emissions"] = True
    return gas_presence


def baseline_first(title_dict, sector, key, data):
    is_baseline = title_dict[sector]["legend"][key][key]["comps"][0][1]
    if is_baseline.find("Baseline") > -1:
        baseline_sector = title_dict[sector]["legend"][key][key]["comps"][0][0]
        base_cols = (data == baseline_sector).any()
        other_cols = (data != baseline_sector).all()
        base_indices = data.loc[:, base_cols].columns.to_list()
        other_indices = data.loc[:, other_cols].columns.to_list()
        new_order = base_indices + other_indices
        data = data.iloc[:, new_order]
    return data


def get_ind(title_dict, sector, key, data, column, subsector):
    # for tup in range(len(title_dict[sector]['legend'][data.loc['Data source'][column]]['comps'])):
    #     subsector = tup[0]
    #     print(int(np.where([title_dict[sector]['legend'][data.loc['Data source'][column]]['comps'][tup][0] == subsector])))

    ind = int(
        np.where(
            [
                title_dict[sector]["legend"][key][data.loc["Data source"][column]][
                    "comps"
                ][tup][0]
                == subsector
                for tup in range(
                    len(
                        title_dict[sector]["legend"][key][
                            data.loc["Data source"][column]
                        ]["comps"]
                    )
                )
            ]
        )[0]
    )
    return ind


def get_params(
    title_dict,
    sector,
    key,
    data,
    column,
    subsector,
    trace_type,
    stack_group,
    co2eq,
    numerical_data,
    comparison_years,
    data_present,
    nonzero_emissions,
    plot_type,
    gwp,
):

    if not data_present:
        empty_message = " (no data)"
    elif not nonzero_emissions:
        empty_message = " (estimate is zero)"
    else:
        empty_message = "placeholder"

    x, y, points = get_x_and_y(numerical_data, comparison_years)

    if title_dict[sector]["title"].find("Metamodeling") > -1:
        if data.loc["Data source"][column] in color_dictionary.keys():
            color_type = data.loc["Data source"][column]
        else:
            color_type = key
    else:
        color_type = key

    if (
        trace_type == "subsector_addition"
        or trace_type == "subsector_subtraction"
        or (trace_type == "empty" and plot_type != "gases")
    ):
        ind = get_ind(title_dict, sector, key, data, column, subsector)
        subsector_name = (
            f"{title_dict[sector]['legend'][key][data.loc['Data source'][column]]['comps'][ind][1]}"
            + f"{title_dict[sector]['legend'][key][data.loc['Data source'][column]]['desc']} {subsector}"
        )
    else:
        subsector_name = "placeholder"

    if trace_type == "gas_plot" or (trace_type == "empty" and plot_type == "gases"):
        gas_name = get_gas_title(data.loc["Gas", column])
    else:
        gas_name = "placeholder"

    mode_by_co2eq = {
        "none": "lines",
        "100-year": "lines",
        "20-year": "lines",
        "both": line_dictionary[gwp],
    }

    gwp_dict = {"both": f" {gwp} GWP", "100-year": "", "20-year": "", "none": ""}

    hover_params = {"namelength": 0, "font_family": "Foros, medium"}
    traces_dict = {
        "subsector_addition": {
            "x": x,
            "y": y,
            "name": subsector_name,
            "hovertext": subsector_name + gwp_dict[co2eq],
            "mode": mode_by_co2eq[co2eq],
            "line": {"color": color_dictionary[color_type], "width": 2, "dash": "dash"},
            "fillcolor": "rgba(0,0,0,0)",
            "fill": "tonexty",
            "stackgroup": stack_group,
            "legendgroup": stack_group,
            "legendrank": legend_rank[key],
            "hoverlabel": hover_params,
            "visible": visibility[key],
        },
        "subsector_subtraction": {
            "x": x,
            "y": y,
            "name": subsector_name,
            "hovertext": subsector_name + gwp_dict[co2eq],
            "mode": mode_by_co2eq[co2eq],
            "line": {"color": color_dictionary[color_type], "width": 1, "dash": "dot"},
            "fillcolor": "rgba(0,0,0,0)",
            "fill": "tonexty",
            "stackgroup": stack_group,
            "legendgroup": stack_group,
            "legendrank": legend_rank[key],
            "hoverlabel": hover_params,
            "visible": visibility[key],
        },
        "total": {
            "x": x,
            "y": y,
            "name": total_title[key] + gwp_dict[co2eq],
            "hovertext": total_title[key] + gwp_dict[co2eq],
            "mode": mode_by_co2eq[co2eq],
            "line": {"color": color_dictionary[key], "width": 3},
            "fillcolor": "rgba(0,0,0,0)",
            "fill": "tonexty",
            "legendgroup": stack_group,
            "legendrank": legend_rank[key],
            "hoverlabel": hover_params,
            "visible": visibility[key],
        },
        "gas_plot": {
            "x": x,
            "y": y,
            "name": gas_name,
            "hovertext": gas_name + gwp_dict[co2eq],
            "mode": mode_by_co2eq[co2eq],
            "line": {
                "color": color_dictionary[color_type],
                "width": 2,
                "dash": gas_lines[data.loc["Gas", column]],
            },
            "fillcolor": "rgba(0,0,0,0)",
            "fill": "tonexty",
            "stackgroup": stack_group,
            "legendgroup": stack_group,
            "legendrank": legend_rank[key],
            "hoverlabel": hover_params,
            "visible": visibility[key],
        },
        "empty": {
            "x": x,
            "y": y,
            "name": subsector_name + empty_message,
            "mode": "lines",
            "line": {"color": "rgba(0,0,0,0)"},
            "legendgroup": stack_group,
            "legendrank": legend_rank[key],
            "visible": "legendonly",
        },
    }
    params = traces_dict[trace_type]
    return params, points, color_type


def get_numerical_addition(
    data_present, nonzero_emissions, data, comparison_years, column, title_dict, sector
):
    data_present = True
    nonzero_emissions = True
    startyear = comparison_years[0]
    endyear = comparison_years[-1]

    if data.loc[comparison_years, column].isnull().all():
        data_present = False
    elif data.loc[comparison_years, column].sum() == 0:
        nonzero_emissions = False
    numerical_data = data.loc[comparison_years, column].replace(0, np.nan).to_list()

    if title_dict[sector]["title"].find("Metamodeling") > -1:
        if key in missing_years.keys():
            missingyrs = list(range(startyear, 2016)) + list(
                range(missing_years["edgar"], endyear)
            )
            missingyrs = [
                comparison_years.index(missingyrs) for missingyrs in missingyrs
            ]
            missingyrs = np.array(missingyrs)
            numerical_data = np.array(numerical_data)
            numerical_data[missingyrs] = np.nan
            numerical_data = numerical_data.tolist()

    return numerical_data, nonzero_emissions, data_present


# def get_numerical_data(
#     data,
#     comparison_years,
#     column,
#     item,
#     key,
#     title_dict,
#     sector,
#     nonzero_emissions,
#     data_present,
# ):
#     data_present = True
#     nonzero_emissions = True
#     startyear = comparison_years[0]
#     endyear = comparison_years[-1]
#     if data.loc[comparison_years, column].isnull().all():
#         data_present = False
#     elif data.loc[comparison_years, column].sum() == 0:
#         nonzero_emissions = False
#
#         # Filter for year rows
#     year_rows = [row for row in data.index if str(row).isdigit()]
#     numerical_data = data.loc[year_rows, column].replace(0, np.nan).tolist()
#
#     missingyrs = np.where(
#         [
#             item[item["Data source"] == key][year_rows].isnull().all()
#             for comparison_years in item[year_rows]
#         ]
#     )[0]
#     numerical_data = np.array(numerical_data)
#     numerical_data[missingyrs] = np.nan
#     numerical_data = numerical_data.tolist()
#
#     if key in missing_years.keys():
#         missingyrs = list(range(missing_years[key], endyear))
#         missingyrs = [comparison_years.index(missingyrs) for missingyrs in missingyrs]
#         missingyrs = np.array(missingyrs)
#         numerical_data = np.array(numerical_data)
#         numerical_data[missingyrs] = np.nan
#         numerical_data = numerical_data.tolist()
#
#     if title_dict[sector]["title"].find("Metamodeling") > -1:
#         if key in missing_years.keys():
#             missingyrs = list(range(startyear, 2016)) + list(
#                 range(missing_years["edgar"], endyear)
#             )
#             missingyrs = [
#                 comparison_years.index(missingyrs) for missingyrs in missingyrs
#             ]
#             missingyrs = np.array(missingyrs)
#             numerical_data = np.array(numerical_data)
#             numerical_data[missingyrs] = np.nan
#             numerical_data = numerical_data.tolist()
#
#     return numerical_data, nonzero_emissions, data_present


#


def get_x_and_y(numerical_data, comparison_years):
    startyear = comparison_years[0]
    endyear = comparison_years[-1]

    if all(np.isnan(numerical_data)):
        x = [startyear]
        y = [0]
        points = []
    else:
        trace_df = {"year": comparison_years, "emissions": numerical_data}
        trace_df = pd.DataFrame(trace_df)
        points = []
        for row in list(range(len(trace_df))):
            if row == 0:
                if np.logical_not(np.isnan(trace_df.iloc[row, 1])) and np.isnan(
                    trace_df.iloc[row + 1, 1]
                ):
                    points.append(trace_df.iloc[row])
                    continue
            elif row == len(trace_df) - 1:
                if np.isnan(trace_df.iloc[row - 1, 1]) and np.logical_not(
                    np.isnan(trace_df.iloc[row, 1])
                ):
                    points.append(trace_df.iloc[row])
                    continue
            elif np.isnan(trace_df.iloc[row - 1, 1]) and np.isnan(
                trace_df.iloc[row + 1, 1]
            ):
                if np.logical_not(np.isnan(trace_df.iloc[row, 1])):
                    points.append(trace_df.iloc[row])
        x = np.array(comparison_years[:])[
            np.where(np.logical_not(np.isnan(numerical_data[:])))[0]
        ]
        y = np.array(numerical_data[:])[
            np.where(np.logical_not(np.isnan(numerical_data[:])))[0]
        ]
    return x, y, points


def get_missing_subsector_params(title_dict, comparison_years, sector, key, comp):
    startyear = comparison_years[0]
    endyear = comparison_years[-1]
    subsector_name = (
        f"{comp[1]} " f"{title_dict[sector]['legend'][key][key]['desc']} " f"{comp[0]}"
    )
    missing_subsector_params = {
        "x": [startyear],
        "y": [0],
        "name": subsector_name + " No Data",
        "mode": "lines",
        "line": {"color": "rgba(0,0,0,0)"},
        "legendgroup": key,
        "legendrank": legend_rank[key],
        "visible": "legendonly",
    }
    return missing_subsector_params


def get_missing_gas_params(key, comparison_years, formula, gas_presence):
    startyear = comparison_years[0]
    endyear = comparison_years[-1]
    gas_name = get_gas_title(formula)
    if not gas_presence[formula]["data_present"]:
        empty_message = " (no data)"
    elif not gas_presence[formula]["nonzero_emissions"]:
        empty_message = " (estimate is zero)"
    missing_gas_params = {
        "x": [startyear],
        "y": [0],
        "name": gas_name + empty_message,
        "mode": "lines",
        "line": {"color": "rgba(0,0,0,0)"},
        "legendgroup": key,
        "legendrank": legend_rank[key],
        "visible": "legendonly",
    }
    return missing_gas_params


def get_points_params(plot_type, color_type, point_symbol, params, co2eq, trace_type):
    try:
        selector_type = {
            "subsectors": {
                "both": {
                    "total": {"name": params["name"]},
                    "subsector_addition": {
                        "name": params["name"],
                        "stackgroup": params["stackgroup"],
                    },
                    "subsector_subtraction": {
                        "name": params["name"],
                        "stackgroup": params["stackgroup"],
                    },
                },
                "100-year": {
                    "total": {"name": params["name"]},
                    "subsector_addition": {"name": params["name"]},
                    "subsector_subtraction": {"name": params["name"]},
                },
                "20-year": {
                    "total": {"name": params["name"]},
                    "subsector_addition": {"name": params["name"]},
                    "subsector_subtraction": {"name": params["name"]},
                },
                "none": {
                    "total": {"name": params["name"]},
                    "subsector_addition": {"name": params["name"]},
                    "subsector_subtraction": {"name": params["name"]},
                },
            },
            "gases": {
                "both": {
                    "total": {"name": params["name"]},
                    "gas_plot": {
                        "name": params["name"],
                        "legendgroup": params["legendgroup"],
                        "stackgroup": params["stackgroup"],
                    },
                },
                "100-year": {
                    "total": {"name": params["name"]},
                    "gas_plot": {
                        "name": params["name"],
                        "legendgroup": params["legendgroup"],
                    },
                },
                "20-year": {
                    "total": {"name": params["name"]},
                    "gas_plot": {
                        "name": params["name"],
                        "legendgroup": params["legendgroup"],
                    },
                },
                "none": {
                    "total": {"name": params["name"]},
                    "gas_plot": {
                        "name": params["name"],
                        "legendgroup": params["legendgroup"],
                    },
                },
            },
        }

        select_params = selector_type[plot_type][co2eq][trace_type]
        points_update = {
            "mode": "lines+markers",
            "marker_symbol": point_symbol,
            "line": {"color": "#d0d6dc"},
            "marker": {"color": color_dictionary[color_type], "size": 12},
            "selector": select_params,
        }
    except KeyError:
        select_params = {"name": params["name"]}
        points_update = {
            "mode": "lines+markers",
            "marker_symbol": point_symbol,
            "line": {"color": "#d0d6dc"},
            "marker": {"color": color_dictionary[color_type], "size": 12},
            "selector": select_params,
        }
    return points_update
