from compare.compare.subtract_out.util.constants import (get_country_title)
from compare.compare.subtract_out.util.country_lists import (countries_annex1, countries_nonannex1)
import pandas as pd
import numpy as np
import copy as copy
from compare.compare.subtract_out.util.generate_plots import plot

def combine_data(temp_dict, country):
    combo_df = pd.DataFrame()
    available = True
    if len(temp_dict) == 0:
        available = False
    else:
        for key, item in temp_dict.items():
            comparison_years = list(item.filter(regex='\d').columns)
            COMP_COLS = ['Data source', 'ID', 'Sector', 'Gas', 'Unit', 'carbon_eq'] + comparison_years

            df = item[item.ID == f'{country}'].reset_index(drop=True)
            available = True
            if df.empty:
                print(f"No data available for {key.upper()} in {country.upper()}")
                available = False
                continue

            df['carbon_eq'] = "none"
            # df = df[COMP_COLS]

            hundred_yr = copy.deepcopy(df)
            hundred_cols = hundred_yr.filter(regex='\d').columns
            hundred_yr.loc[hundred_yr['Gas'] == 'ch4', hundred_cols] = hundred_yr.loc[hundred_yr['Gas'] == 'ch4', hundred_cols] * 28
            hundred_yr.loc[hundred_yr['Gas'] == 'n2o', hundred_cols] = hundred_yr.loc[hundred_yr['Gas'] == 'n2o', hundred_cols] * 265
            hundred_yr['carbon_eq'] = '100-year'

            twenty_yr = copy.deepcopy(df)
            twenty_cols = twenty_yr.filter(regex='\d').columns
            twenty_yr.loc[twenty_yr['Gas'] == 'ch4', twenty_cols] = twenty_yr.loc[twenty_yr['Gas'] == 'ch4', twenty_cols] * 84
            twenty_yr.loc[twenty_yr['Gas'] == 'n2o', twenty_cols] = twenty_yr.loc[twenty_yr['Gas'] == 'n2o', twenty_cols] * 264
            twenty_yr['carbon_eq'] = '20-year'

            combo_df = pd.concat([combo_df, df, hundred_yr, twenty_yr])

        if not combo_df.empty:
            totals_df = combo_df.groupby(['Gas', 'carbon_eq'], as_index = False).sum(min_count=1)
            totals_df['Sector'] = 'Subtotal'
            totals_df['ID'] = country
            totals_df['Unit'] = 'tonnes'
            totals_df['Data source'] = 'gapfilled'
            totals_df = totals_df[COMP_COLS]

            grand_totals = totals_df.groupby('carbon_eq', as_index = False).sum(min_count=1)
            grand_totals['Gas'] = 'co2e'
            grand_totals['Sector'] = 'Total'
            grand_totals['ID'] = country
            grand_totals['Unit'] = 'tonnes'
            grand_totals['Data source'] = 'gapfilled'
            grand_totals = grand_totals[COMP_COLS]

            subsector_df = combo_df.groupby(['Sector', 'carbon_eq', 'Data source'], as_index=False).sum(min_count=1)
            subsector_df['Gas'] = 'co2e'
            subsector_df['ID'] = country
            subsector_df['Unit'] = 'tonnes'
            subsector_df = subsector_df[COMP_COLS]

            combo_df = pd.concat([combo_df, totals_df, subsector_df, grand_totals])

    return combo_df, available


def compare(comparison_dict, country, allinv, sector, ratio_data):
    plotting_dict = {}
    for compare_inventory, subinvdict in comparison_dict.items():
        print(f"Calculating comparison to {compare_inventory.upper()} {sector} {country}")
        temp_dict = {}
        for subinv, termdetails in subinvdict.items():
            print(f"       Manipulating data from {subinv.upper()}")
            for tup in termdetails:
                df = allinv[(allinv.Sector == f"{tup[0]}") & (allinv['Data source'] == f"{subinv}")].copy()
                if not df.empty:
                    data_cols = df.filter(regex='\d').columns
                    df.loc[:, data_cols] = df.loc[:, data_cols] * tup[1]
                    temp_dict[f"{tup[0]}"] = df
            combo_df, available = combine_data(temp_dict, country)
        plotting_dict[compare_inventory] = combo_df
        if available:
            ratio_agg = combo_df.loc[(combo_df['carbon_eq'] == '100-year') &
                         ((combo_df['Sector'] == 'Subtotal')|(combo_df['Sector'] == 'Total'))].copy()
            ratio_agg['Data source'] = compare_inventory
            ratio_agg['Sector'] = sector
            ratio_data = pd.concat([ratio_data, ratio_agg])
    return plotting_dict, ratio_data


def create_plots(allinv, countries, sector, gas, co2eq, plot_type, ratio_data, output_folder, comparison_dicts, title_dicts):

    for country in countries:
        if country is np.nan:
            continue
        if country in countries_annex1:
            master_comparison_dict = comparison_dicts['annex1']
            title_dict = title_dicts['annex1']
        elif country in countries_nonannex1:
            master_comparison_dict = comparison_dicts['nonannex1']
            title_dict = title_dicts['nonannex1']
        else:
            master_comparison_dict = comparison_dicts['nonannex1']

        try:
            comparison_dict = master_comparison_dict[sector]
        except KeyError:
            print(f'Calculated comparison not available for {sector} in {country}')
            continue

        plotting_dict, ratio_data = compare(comparison_dict, country, allinv, sector, ratio_data)

        if not (all(plotting_dict[d].empty for d in plotting_dict.keys()) or plotting_dict['climate-trace'].empty):
            try:
                plot(sector, country, gas, co2eq, plot_type, title_dict, output_folder, plotting_dict)
            except AttributeError:
                print(f'Attribute missing for {sector} in {country} plot')
                continue
        else:
            print(f'No data to plot for {sector} in {country}')

    return ratio_data

