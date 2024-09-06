"""This module contains the function, plot, that will build the plots that are called in SectorComparison from
subtract_out_plotting.py"""

from climate_trace_tools.compare.subtract_out.util.constants import get_country_title
import plotly
import plotly.graph_objects as go
import plotly.offline
import numpy as np
import os
from climate_trace_tools.compare.subtract_out.util.logger_setup import logger
from climate_trace_tools.compare.subtract_out.util.plotting_utils import (
    get_layout,
    fonts,
    get_yaxes,
    xaxes,
    is_data_present,
    get_legend_title_params,
    # get_numerical_data,
    get_params,
    gwp_list,
    get_missing_subsector_params,
    is_gas_present,
    get_numerical_addition,
    get_missing_gas_params,
    get_point_symbol,
    annotation,
    baseline_first,
    get_points_params,
)


def split_data(comparison_years, numerical_data, is_forward_filled):
    true_x, true_y, ff_x, ff_y = [], [], [], []
    for year, value, ff in zip(comparison_years, numerical_data, is_forward_filled):
        if ff:
            ff_x.append(year)
            ff_y.append(value)
        else:
            true_x.append(year)
            true_y.append(value)
    return true_x, true_y, ff_x, ff_y


# The is_valid_data_column function
def is_valid_data_column(data, column, gas, gwp):
    """
    Determine if a data column is valid for plotting based on gas and GWP settings.

    Args:
        data (pd.DataFrame): The data being processed.
        column (str or int): The current column being processed.
        gas (str): The gas type being plotted ('all' or a specific gas).
        gwp (str): The Global Warming Potential setting.

    Returns:
        bool: True if the column is valid for plotting, False otherwise.
    """
    try:
        gas_value = data.loc["Gas"].iloc[column]
        carbon_eq_value = (
            data.loc["carbon_eq"].iloc[column] if "carbon_eq" in data.index else None
        )

        if gas == "all":
            return gas_value == "co2e" and (
                carbon_eq_value == gwp or carbon_eq_value is None
            )
        else:
            return gas_value == gas and (
                carbon_eq_value == gwp or carbon_eq_value is None
            )
    except (KeyError, IndexError, AttributeError) as e:
        print(f"Error in is_valid_data_column: {e}")
        return False


def plot(
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
):
    fig = initialize_figure(country, title_dict, sector, gas, co2eq)

    if not should_plot(plotting_dict):
        logger.debug(
            f"None of the comparison inventories have data available to compare or {sector}"
        )
        return

    comparison_years = list(plotting_dict["climate-trace"].filter(regex="\d").columns)

    for key, item in plotting_dict.items():
        if not process_inventory(
            fig, key, item, title_dict, comparison_years, sector, gas, co2eq, plot_type
        ):
            continue

    save_plot(fig, output_folder, country, sector, plot_type, create_folders, plot_live)


def process_inventory(
    fig, key, item, title_dict, comparison_years, sector, gas, co2eq, plot_type
):
    data_present, nonzero_emissions = is_data_present(item, key)
    if key == "climate-trace" and (not data_present or not nonzero_emissions):
        return False

    item.reset_index(inplace=True)
    data = item.transpose()
    add_legend_title(
        fig, title_dict, comparison_years, sector, key, data_present, nonzero_emissions
    )

    for gwp in gwp_list[co2eq]:
        if plot_type == "subsectors":
            process_subsectors(
                fig,
                data,
                key,
                title_dict,
                comparison_years,
                sector,
                gas,
                co2eq,
                gwp,
                data_present,
                nonzero_emissions,
            )
        elif plot_type == "gases":
            process_gases(
                fig,
                data,
                key,
                item,
                title_dict,
                comparison_years,
                sector,
                gas,
                co2eq,
                gwp,
                data_present,
                nonzero_emissions,
            )

    return True


def process_subsectors(
    fig,
    data,
    key,
    title_dict,
    comparison_years,
    sector,
    gas,
    co2eq,
    gwp,
    data_present,
    nonzero_emissions,
):
    for column in data.columns:
        if not is_valid_data_column(data, column, gas, gwp):
            continue

        numerical_data, is_forward_filled = get_data_for_column(
            data, comparison_years, column, key, title_dict, sector
        )
        true_x, true_y, ff_x, ff_y = split_data(
            comparison_years, numerical_data, is_forward_filled
        )

        params = get_trace_params(
            data,
            column,
            key,
            title_dict,
            sector,
            co2eq,
            gwp,
            numerical_data,
            comparison_years,
            data_present,
            nonzero_emissions,
        )

        add_trace(fig, true_x, true_y, ff_x, ff_y, params, key)


def get_data_for_column(data, comparison_years, column, key, title_dict, sector):
    if is_addition_case(data, column, key, title_dict, sector):
        numerical_data, _, _ = get_numerical_addition(
            True, True, data, comparison_years, column, title_dict, sector
        )
    else:
        numerical_data, _, _ = get_numerical_addition(
            True, True, data, comparison_years, column, title_dict, sector
        )
    ff_indexes = list(data.filter(regex=r"^\d+_ff$", axis=0).index)
    is_forward_filled = [data.loc[index, column] for index in ff_indexes]
    # is_forward_filled = [data.loc[f"{year}_ff", column] for year in comparison_years]
    return numerical_data, is_forward_filled


def prepare_trace_data(x, y):
    """Prepare data for plotting by removing NaN values."""
    valid_indices = ~np.isnan(y)
    return np.array(x)[valid_indices], np.array(y)[valid_indices]


def add_trace(fig, true_x, true_y, ff_x, ff_y, params, key):
    # Add trace for true data
    logger.debug(f"Received params: {params}")
    logger.debug(f"Params type: {type(params)}")

    if not isinstance(params, tuple) or len(params) != 3:
        logger.error(
            f"Expected params to be a tuple of length 3, but got {type(params)} of length {len(params) if isinstance(params, tuple) else 'N/A'}"
        )
        return

    trace_params, points, color_type = params

    if not isinstance(trace_params, dict):
        logger.error(
            f"Expected first element of params to be a dictionary, but got {type(trace_params)}"
        )
        return

    # Extract values from the trace_params dictionary
    name = trace_params.get("name", "")
    mode = trace_params.get("mode", "lines")
    line = trace_params.get("line", {"color": "blue", "width": 2})
    fillcolor = trace_params.get("fillcolor", None)
    fill = trace_params.get("fill", None)
    stackgroup = trace_params.get("stackgroup", None)
    legendgroup = trace_params.get("legendgroup", None)
    legendrank = trace_params.get("legendrank", None)
    hoverlabel = trace_params.get("hoverlabel", None)
    visible = trace_params.get("visible", True)

    # Combine true and forward-filled data
    x = true_x + ff_x
    y = true_y + ff_y

    # Create a list to track which points are forward-filled
    is_ff = [False] * len(true_x) + [True] * len(ff_x)

    # Sort all lists based on x values
    sorted_data = sorted(zip(x, y, is_ff))
    x = [item[0] for item in sorted_data]
    y = [item[1] for item in sorted_data]
    is_ff = [item[2] for item in sorted_data]

    # Prepare data for true values
    plot_x, plot_y = prepare_trace_data(x, y)
    # Create hover text
    hovertext = [
        f"{x[i]}<br>{y[i]:.2f}" + (" (forward-filled)" if is_ff[i] else "")
        for i in range(len(x))
    ]
    # Check if all y values are NaN
    all_nan = all(np.isnan(y_val) for y_val in y)

    if all_nan:
        # If all values are NaN, create a trace that only appears in the legend
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                name=name + " (No Data)",
                mode="lines",
                line=line,
                legendgroup=legendgroup,
                legendrank=legendrank,
                visible=visible,
                hoverinfo="none",
            )
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=plot_x,
                y=plot_y,
                name=f"{name}",
                mode=mode,
                line=line,
                fillcolor=fillcolor,
                fill=fill,
                stackgroup=stackgroup,
                legendgroup=legendgroup,
                legendrank=legendrank,
                # hoverlabel=hoverlabel,
                visible=visible,
                marker=dict(
                    color=[
                        line["color"] if not ff else "rgba(255,255,255,1)"
                        for ff in is_ff
                    ],
                    size=[6 if not ff else 8 for ff in is_ff],
                    symbol=["circle" if not ff else "circle-open" for ff in is_ff],
                    line=dict(
                        width=[0 if not ff else 2 for ff in is_ff], color=line["color"]
                    ),
                ),
                text=hovertext,
                hoverinfo="text",
                hovertemplate="%{text}<extra></extra>",
            )
        )


# Helper functions
def initialize_figure(country, title_dict, sector, gas, co2eq):
    """
    Initialize a plotly figure with the appropriate layout and axes.

    Args:
        country (str): The country for which the plot is being created.
        title_dict (dict): Dictionary containing title information.
        sector (str): The sector being plotted.
        gas (str): The gas type being plotted.
        co2eq (str): The CO2 equivalent setting.

    Returns:
        plotly.graph_objs.Figure: An initialized plotly Figure object.
    """

    layout = get_layout(country, title_dict, sector)
    fig = go.Figure(layout=go.Layout(**layout)).update_layout(font=fonts)
    yaxes = get_yaxes(gas, co2eq)
    fig.update_yaxes(**yaxes).update_xaxes(**xaxes)
    fig.add_annotation(**annotation)
    return fig


def should_plot(plotting_dict):
    """
    Determine if there is sufficient data to create a plot.

    Args:
        plotting_dict (dict): Dictionary containing plotting data for different inventories.

    Returns:
        bool: True if there is sufficient data to plot, False otherwise.
    """
    non_zero_sum = {}
    data_present_sum = {}
    for inventory, item in plotting_dict.items():
        data_present, nonzero_emissions = is_data_present(item, inventory)
        non_zero_sum[inventory] = nonzero_emissions
        data_present_sum[inventory] = data_present

    return (
        (sum(non_zero_sum.values()) > 1)
        and ("climate-trace" in non_zero_sum.keys())
        and (sum(data_present_sum.values()) > 1)
    )


def add_legend_title(
    fig, title_dict, comparison_years, sector, key, data_present, nonzero_emissions
):
    """
    Add a legend title to the plot.

    Args:
        fig (plotly.graph_objs.Figure): The figure to add the legend title to.
        title_dict (dict): Dictionary containing title information.
        comparison_years (list): List of years being compared.
        sector (str): The sector being plotted.
        key (str): The key for the current inventory.
        data_present (bool): Whether data is present for this inventory.
        nonzero_emissions (bool): Whether non-zero emissions are present for this inventory.
    """
    legend_title_params = get_legend_title_params(
        title_dict, comparison_years, sector, key, data_present, nonzero_emissions
    )
    fig.add_trace(go.Scatter(**legend_title_params))


def process_gases(
    fig,
    data,
    key,
    item,
    title_dict,
    comparison_years,
    sector,
    gas,
    co2eq,
    gwp,
    data_present,
    nonzero_emissions,
):
    """
    Process and plot gas-related data.

    Args:
        fig (plotly.graph_objs.Figure): The figure to add the traces to.
        data (pd.DataFrame): The data to be processed.
        key (str): The key for the current inventory.
        item (pd.DataFrame): The full dataset for the current inventory.
        title_dict (dict): Dictionary containing title information.
        comparison_years (list): List of years being compared.
        sector (str): The sector being plotted.
        gas (str): The gas type being plotted.
        co2eq (str): The CO2 equivalent setting.
        gwp (str): The Global Warming Potential setting.
        data_present (bool): Whether data is present for this inventory.
        nonzero_emissions (bool): Whether non-zero emissions are present for this inventory.
    """
    gas_presence = is_gas_present(key, item)
    for formula in gas_presence.keys():
        for data_status in gas_presence[formula]:
            if not gas_presence[formula][data_status]:
                params = get_missing_gas_params(
                    key, comparison_years, formula, gas_presence
                )
                fig.add_trace(go.Scatter(**params))

    for column in data.columns:
        if not (
            data.loc["Data source", column] == "gapfilled"
            and data.loc["carbon_eq", column] == gwp
        ):
            continue

        stack_group = f"{key}{gwp}" if co2eq == "both" else key
        subsector = "placeholder"

        if data.loc["Sector"][column] in ["Subtotal", "Total"]:
            numerical_data, nonzero_emissions, data_present = get_numerical_addition(
                True, True, data, comparison_years, column, title_dict, sector
            )
            if (
                all(np.isnan(numerical_data))
                and data.loc["Sector"][column] == "Subtotal"
            ):
                continue

            trace_type = (
                "gas_plot" if data.loc["Sector"][column] == "Subtotal" else "total"
            )

            params, points, color_type = get_params(
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
                "gases",
                gwp,
            )
            fig.add_trace(go.Scatter(**params))
            if len(points) > 0:
                points_update = get_points_params(
                    "gases",
                    color_type,
                    get_point_symbol(co2eq, gwp),
                    params,
                    co2eq,
                    trace_type,
                )
                fig.update_traces(**points_update)


def is_addition_case(data, column, key, title_dict, sector):
    """
    Determine if the current data should be treated as an addition case.

    Args:
        data (pd.DataFrame): The data being processed.
        column (str): The current column being processed.
        key (str): The key for the current inventory.
        title_dict (dict): Dictionary containing title information.
        sector (str): The sector being plotted.

    Returns:
        bool: True if it's an addition case, False otherwise.
    """
    return (
        data.loc["Data source"][column] == key
        and data.loc["Data source"][column] != "gapfilled"
        and title_dict[sector]["title"].find("Metamodeling") == -1
    ) or (
        data.loc["Data source"][column] == "edgar"
        and title_dict[sector]["title"].find("Metamodeling") > -1
    )


def get_trace_params(
    data,
    column,
    key,
    title_dict,
    sector,
    co2eq,
    gwp,
    numerical_data,
    comparison_years,
    data_present,
    nonzero_emissions,
):
    """
    Get the parameters for adding a trace to the plot.

    Args:
        data (pd.DataFrame): The data being processed.
        column (str): The current column being processed.
        key (str): The key for the current inventory.
        title_dict (dict): Dictionary containing title information.
        sector (str): The sector being plotted.
        co2eq (str): The CO2 equivalent setting.
        gwp (str): The Global Warming Potential setting.
        numerical_data (list): The numerical data for the trace.
        comparison_years (list): List of years being compared.
        data_present (bool): Whether data is present for this inventory.
        nonzero_emissions (bool): Whether non-zero emissions are present for this inventory.

    Returns:
        tuple: A tuple containing the trace parameters, points, and color type.
    """
    subsector = data.loc["Sector", column]
    stack_group = f"{key}{gwp}" if co2eq == "both" else key

    if is_addition_case(data, column, key, title_dict, sector):
        trace_type = (
            "subsector_addition" if not all(np.isnan(numerical_data)) else "empty"
        )
    elif data.loc["Data source"][column] != "gapfilled":
        trace_type = (
            "subsector_subtraction" if not all(np.isnan(numerical_data)) else "empty"
        )
    else:
        trace_type = "total"

    params, points, color_type = get_params(
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
        "subsectors",
        gwp,
    )

    return params, points, color_type


def save_plot(
    fig, output_folder, country, sector, plot_type, create_folders, plot_live
):
    """
    Save the plot to a file.

    Args:
        fig (plotly.graph_objs.Figure): The figure to be saved.
        output_folder (str): The folder where the plot should be saved.
        country (str): The country for which the plot is being created.
        sector (str): The sector being plotted.
        plot_type (str): The type of plot being created.
        create_folders (bool): Whether to create output folders if they don't exist.
        plot_live (bool): Whether to open the plot in a browser after saving.
    """
    if create_folders:
        try:
            os.makedirs(output_folder + "/", exist_ok=True)
            logger.debug("Output folder created or already exists.")
        except Exception as e:
            logger.error(f"Error creating output folder: {str(e)}")
            return

    plot_file = (
        f"{output_folder}/{get_country_title(country)}_{sector}_{plot_type}.html"
    )
    try:
        plotly.offline.plot(fig, filename=plot_file, auto_open=plot_live)
        logger.info(f"Plot file created: {plot_file}")
    except Exception as e:
        logger.error(f"Error saving plot: {str(e)}")
