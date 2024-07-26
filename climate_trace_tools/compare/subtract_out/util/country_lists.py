# Country lists


countries_annex1 = [
    "AUS",
    "AUT",
    "BLR",
    "BEL",
    "BGR",
    "CAN",
    "HRV",
    "CYP",
    "CZE",
    "DNK",
    "EST",
    "FIN",
    "FRA",
    "DEU",
    "GRC",
    "HUN",
    "ISL",
    "IRL",
    "ITA",
    "JPN",
    "KAZ",
    "LVA",
    "LIE",
    "LTU",
    "LUX",
    "MLT",
    "MCO",
    "NLD",
    "NZL",
    "NOR",
    "POL",
    "PRT",
    "ROU",
    "RUS",
    "SVK",
    "SVN",
    "ESP",
    "SWE",
    "CHE",
    "TUR",
    "UKR",
    "GBR",
    "USA",
]
countries_nonannex1 = [
    "ABW",
    "AFG",
    "ALB",
    "DZA",
    "AGO",
    "ATG",
    "ARG",
    "ARM",
    "AZE",
    "BHS",
    "BHR",
    "BGD",
    "BRA",
    "BRB",
    "BLZ",
    "BEN",
    "BTN",
    "BOL",
    "BIH",
    "BWA",
    "BRN",
    "BFA",
    "BDI",
    "CPV",
    "KHM",
    "CMR",
    "CAF",
    "CHL",
    "CHN",
    "COL",
    "COM",
    "COG",
    "CRI",
    "CIV",
    "CUB",
    "PRK",
    "COD",
    "DJI",
    "DMA",
    "DOM",
    "ECU",
    "EGY",
    "SLV",
    "ERI",
    "SWZ",
    "HKG",
    "ETH",
    "FJI",
    "GAB",
    "GMB",
    "GEO",
    "GHA",
    "GRD",
    "GTM",
    "GIN",
    "GNB",
    "GUY",
    "HTI",
    "HND",
    "IDN",
    "IND",
    "IRN",
    "IRQ",
    "ISR",
    "JAM",
    "JOR",
    "KEN",
    "KIR",
    "KWT",
    "KGZ",
    "LAO",
    "LBN",
    "LSO",
    "LBR",
    "MDG",
    "MWI",
    "MYS",
    "MDV",
    "MLI",
    "MHL",
    "MRT",
    "MUS",
    "MEX",
    "FSM",
    "MNG",
    "MNE",
    "MAR",
    "MOZ",
    "MMR",
    "NAM",
    "NRU",
    "NPL",
    "NIC",
    "NER",
    "NGA",
    "NIU",
    "MKD",
    "OMN",
    "PLW",
    "PAN",
    "PRY",
    "PER",
    "PHL",
    "QAT",
    "KOR",
    "MDA",
    "RWA",
    "KNA",
    "LCA",
    "VCT",
    "WSM",
    "SMR",
    "STP",
    "SAU",
    "SEN",
    "SRB",
    "SYC",
    "SGP",
    "SLB",
    "ZAF",
    "SSD",
    "LKA",
    "PSE",
    "SDN",
    "TJK",
    "THA",
    "TLS",
    "TGO",
    "TON",
    "TTO",
    "TUN",
    "TKM",
    "TUV",
    "UGA",
    "ARE",
    "TZA",
    "URY",
    "UZB",
    "VUT",
    "VEN",
    "YEM",
    "ZMB",
    "ZWE",
    "TCD",
    "COK",
    "PAK",
    "PNG",
    "SUR",
    "VNM",
    "TWN",
]

# def get_top_thirty(allinv, sectors_to_plot):
#     top30 = {}
#     for sector in sectors_to_plot:
#         comparison_dict = top_30_dict[sector]
#         ranking_dict = {}
#         for compare_inventory, subinvdict in comparison_dict.items():
#             temp_dict = {}
#             for subinv, termdetails in subinvdict.items():
#                 for tup in termdetails:
#                     df = allinv[(allinv.Sector == f"{tup[0]}") & (allinv['Data source'] == f"{subinv}")].copy()
#                     if not df.empty:
#                         data_cols = df.filter(regex='\d').columns
#                         df.loc[:, data_cols] = df.loc[:, data_cols] * tup[1]
#                         temp_dict[f"{tup[0]}"] = df
#                 if len(temp_dict) > 0:
#                     top_emitters_100, top_emitters_20 = combine_ranking_data(temp_dict)
#                     all_top = np.unique(top_emitters_100 + top_emitters_20).tolist()
#                 else:
#                     all_top = []
#         top30[sector] = all_top
#     return top30

# def combine_ranking_data(temp_dict):
#     combo_df = pd.DataFrame()
#     for key, item in temp_dict.items():
#         df = item
#
#         if df.empty:
#             print(f"No data available for {key.upper()}")
#             continue
#
#         df['carbon_eq'] = "none"
#         df = df[COMP_COLS]
#
#         hundred_yr = copy.deepcopy(df)
#         hundred_cols = hundred_yr.filter(regex='\d').columns
#         hundred_yr.loc[hundred_yr['Gas'] == 'ch4', hundred_cols] = hundred_yr.loc[hundred_yr['Gas'] == 'ch4', hundred_cols] * 28
#         hundred_yr.loc[hundred_yr['Gas'] == 'n2o', hundred_cols] = hundred_yr.loc[hundred_yr['Gas'] == 'n2o', hundred_cols] * 265
#         hundred_yr['carbon_eq'] = '100-year'
#
#         twenty_yr = copy.deepcopy(df)
#         twenty_cols = twenty_yr.filter(regex='\d').columns
#         twenty_yr.loc[twenty_yr['Gas'] == 'ch4', twenty_cols] = twenty_yr.loc[twenty_yr['Gas'] == 'ch4', twenty_cols] * 84
#         twenty_yr.loc[twenty_yr['Gas'] == 'n2o', twenty_cols] = twenty_yr.loc[twenty_yr['Gas'] == 'n2o', twenty_cols] * 264
#         twenty_yr['carbon_eq'] = '20-year'
#
#         combo_df = pd.concat([combo_df, hundred_yr, twenty_yr])
#
#     if not combo_df.empty:
#         totals_df = combo_df.groupby(['Gas', 'carbon_eq', 'ID'], as_index = False).sum(min_count=1)
#         totals_df['Sector'] = 'Subtotal'
#         totals_df['Unit'] = 'tonnes'
#         totals_df['Data source'] = 'gapfilled'
#         totals_df = totals_df[COMP_COLS]
#
#         grand_totals = totals_df.groupby(['carbon_eq', 'ID'], as_index = False).sum(min_count=1)
#         grand_totals['Gas'] = 'co2e'
#         grand_totals['Sector'] = 'Total'
#         grand_totals['Unit'] = 'tonnes'
#         grand_totals['Data source'] = 'gapfilled'
#         grand_totals = grand_totals[COMP_COLS]
#
#         combo_df = pd.concat([combo_df, totals_df, grand_totals])
#
#         if any(combo_df['Data source'] == 'edgar'):
#             top_emitters_100 = grand_totals.loc[grand_totals['carbon_eq'] == '100-year'].nlargest(30, [2018])['ID'].tolist()
#             top_emitters_20 = grand_totals.loc[grand_totals['carbon_eq'] == '20-year'].nlargest(30, [2018])['ID'].tolist()
#         elif all(np.isnan(grand_totals[2021])):
#             top_emitters_100 = grand_totals.loc[grand_totals['carbon_eq'] == '100-year'].nlargest(30, [2020])['ID'].tolist()
#             top_emitters_20 = grand_totals.loc[grand_totals['carbon_eq'] == '20-year'].nlargest(30, [2020])['ID'].tolist()
#         else:
#             top_emitters_100 = grand_totals.loc[grand_totals['carbon_eq'] == '100-year'].nlargest(30, [2021])['ID'].tolist()
#             top_emitters_20 = grand_totals.loc[grand_totals['carbon_eq'] == '20-year'].nlargest(30, [2021])['ID'].tolist()
#
#     return top_emitters_100, top_emitters_20
