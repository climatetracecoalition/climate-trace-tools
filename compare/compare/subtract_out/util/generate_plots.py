from compare.compare.subtract_out.util.constants import (get_country_title)
import plotly
import plotly.graph_objects as go
import plotly.offline
import numpy as np
import os
from compare.compare.subtract_out.util.plotting_utils import (get_layout, fonts, get_yaxes, xaxes, is_data_present,
                                        get_legend_title_params, get_numerical_data, get_params, gwp_list,
                                        get_missing_subsector_params, is_gas_present, get_numerical_addition,
                                        get_missing_gas_params, get_point_symbol, annotation, baseline_first,
                                        get_points_params)


def plot(sector, country, gas, co2eq, plot_type, title_dict, output_folder, plotting_dict):
    
    layout = get_layout(country, title_dict, sector)
    fig = go.Figure(layout=go.Layout(**layout)).update_layout(font=fonts)
    yaxes = get_yaxes(gas, co2eq)
    fig.update_yaxes(**yaxes).update_xaxes(**xaxes)
    fig.add_annotation(**annotation)

    non_zero_sum = {}
    for inventory, item in plotting_dict.items():
        data_present, nonzero_emissions = is_data_present(item, inventory)
        non_zero_sum[inventory] = nonzero_emissions

    if (sum(non_zero_sum.values()) > 1) & ('climate-trace' in non_zero_sum.keys()):
        pass
    else:
        print('No comparison available for chosen inputs')
        return

    dont_plot = False
    for key, item in plotting_dict.items():
        item.reset_index(drop=True, inplace=True)
        data_present, nonzero_emissions = is_data_present(item, key)
        if key == 'climate-trace' and (not data_present or not nonzero_emissions):
            dont_plot = True
            continue

        comparison_years = list(item.filter(regex='\d').columns)
        # comparison_years = list(range(startyear, endyear))
        data = item.transpose()

        legend_title_params = get_legend_title_params(title_dict, comparison_years,sector, key, data_present, nonzero_emissions)
        fig.add_trace(go.Scatter(**legend_title_params))

        gwps = gwp_list[co2eq]

        for gwp in gwps:
            point_symbol = get_point_symbol(co2eq, gwp)
            if plot_type == 'subsectors':
                if not data_present or not nonzero_emissions:
                    for comp in title_dict[sector]['legend'][key][key]['comps']:
                        params = get_missing_subsector_params(title_dict, comparison_years, sector, key, comp)
                        fig.add_trace(go.Scatter(**params))
                if data_present:
                    data = baseline_first(title_dict, sector, key, data)

                for column in data.columns:
                    if gas == 'all':
                        if not (data.loc['Gas', column] == 'co2e' and data.loc['carbon_eq', column] == gwp):
                            continue
                    else:
                        if not (data.loc['Gas', column] == gas and data.loc['carbon_eq', column] == gwp):
                            continue

                    subsector = data.loc['Sector', column]
                    if co2eq == 'both':
                        stack_group = f"{key}{gwp}"
                    else:
                        stack_group = key


                    if (data.loc['Data source'][column] == key and data.loc['Data source'][column] != 'gapfilled' and
                            title_dict[sector]['title'].find('Metamodeling') == -1) or \
                            (data.loc['Data source'][column] == 'edgar' and
                             title_dict[sector]['title'].find('Metamodeling') > -1):
                        numerical_data, nonzero_emissions, data_present = get_numerical_addition(data_present,
                                                                nonzero_emissions, data, comparison_years, column,
                                                                title_dict, sector)
                        if all(np.isnan(numerical_data)):
                            trace_type = 'empty'
                        else:
                            trace_type = 'subsector_addition'
                        
                        params, points, color_type = get_params(title_dict, sector, key, data, column,
                                                                subsector, trace_type, stack_group, co2eq,
                                                                numerical_data, comparison_years, data_present,
                                                                nonzero_emissions, plot_type, gwp)

                    elif data.loc['Data source'][column] != 'gapfilled':
                        numerical_data, nonzero_emissions, data_present = get_numerical_data(data, comparison_years,
                                                                                column, item, key, title_dict, sector,
                                                                                nonzero_emissions, data_present)
                        if all(np.isnan(numerical_data)):
                            trace_type = 'empty'
                        else:
                            trace_type = 'subsector_subtraction'
            
                        params, points, color_type = get_params(title_dict, sector, key, data, column,
                                                                subsector, trace_type, stack_group, co2eq,
                                                                numerical_data, comparison_years, data_present,
                                                                nonzero_emissions, plot_type, gwp)

                    if data.loc['Data source'][column] != 'gapfilled':
                        fig.add_trace(go.Scatter(**params))
                        if len(points) > 0:
                            points_update = get_points_params(plot_type, color_type, point_symbol,
                                                              params, co2eq, trace_type)
                            fig.update_traces(**points_update)

                    if (gas == 'all' and data.loc['Data source'][column] == 'gapfilled') or \
                            (gas != 'all' and data.loc['Data source'][column] == 'gapfilled' and
                             data.loc['Sector'][column] == 'Subtotal'):
                        numerical_data, nonzero_emissions, data_present = get_numerical_data(data, comparison_years,
                                                                                column, item, key, title_dict, sector,
                                                                                nonzero_emissions, data_present)
                        trace_type = 'total'

                        params, points, color_type = get_params(title_dict, sector, key, data, column,
                                                                subsector, trace_type, stack_group, co2eq,
                                                                numerical_data, comparison_years, data_present,
                                                                nonzero_emissions, plot_type, gwp)
                        fig.add_trace(go.Scatter(**params))
                        if len(points) > 0:
                            points_update = get_points_params(plot_type, color_type, point_symbol,
                                                              params, co2eq, trace_type)
                            fig.update_traces(**points_update)

            elif plot_type == 'gases':
                gas_presence = is_gas_present(key, item)
                for formula in gas_presence.keys():
                    for data_status in gas_presence[formula]:
                        if not gas_presence[formula][data_status]:
                            params = get_missing_gas_params(key, comparison_years, formula, gas_presence)
                            fig.add_trace(go.Scatter(**params))

                for column in data.columns:
                    if not (data.loc['Data source', column] == 'gapfilled' and data.loc['carbon_eq', column] == gwp):
                        continue

                    if co2eq == 'both':
                        stack_group = f"{key}{gwp}"
                    else:
                        stack_group = key
                    subsector = 'placeholder'

                    if data.loc['Sector'][column] == 'Subtotal':
                        numerical_data, nonzero_emissions, data_present = get_numerical_data(data, comparison_years,
                                                                                column, item, key, title_dict, sector,
                                                                                nonzero_emissions, data_present)
                        if all(np.isnan(numerical_data)):
                            continue
                        else:
                            trace_type = 'gas_plot'

                        params, points, color_type = get_params(title_dict, sector, key, data, column,
                                                                subsector, trace_type, stack_group, co2eq,
                                                                numerical_data, comparison_years, data_present,
                                                                nonzero_emissions, plot_type, gwp)
                        fig.add_trace(go.Scatter(**params))
                        if len(points) > 0:
                            points_update = get_points_params(plot_type, color_type, point_symbol,
                                                              params, co2eq, trace_type)
                            fig.update_traces(**points_update)

                    elif data.loc['Sector'][column] == 'Total':
                        numerical_data, nonzero_emissions, data_present = get_numerical_data(data, comparison_years,
                                                                                column, item, key, title_dict, sector,
                                                                                nonzero_emissions, data_present)
                        trace_type = 'total'

                        params, points, color_type = get_params(title_dict, sector, key, data, column,
                                                                subsector, trace_type, stack_group, co2eq,
                                                                numerical_data, comparison_years, data_present,
                                                                nonzero_emissions, plot_type, gwp)
                        fig.add_trace(go.Scatter(**params))
                        if len(points) > 0:
                            points_update = get_points_params(plot_type, color_type, point_symbol,
                                                              params, co2eq, trace_type)
                            fig.update_traces(**points_update)
    try:
        os.makedirs(output_folder + '/' + f'{country}')
        print('Output folder created.')
    except OSError:
        print('Output folder already exists.')
    if not dont_plot:
        plotly.offline.plot(fig, filename=f"{output_folder}/{country}/{get_country_title(country)}_{sector}_{plot_type}.html")
        # plotly.offline.plot(fig, filename=f"{output_folder}/{country}", image='png')
