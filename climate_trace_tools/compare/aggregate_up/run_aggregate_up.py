from aggregate_up_plotting import CountryPlotting 
from climate_trace_tools.compare.country_lists import countries_all
from pathlib import Path
import pandas as pd
import datetime


# TO GET GLOBAL COMPARISON TO THE CHOSEN INVENTORY (SEE `inventory` BELOW), BY COUNTRY
# countries_all covers every ISO3 in the countries reference table, not just UNFCCC Parties,
# so territories/dependencies (e.g. Greenland, Puerto Rico) are included in the global total too.
# Filter out any blank/falsy entries: CsvDataHandler.load_by_sector_country only filters when
# `iso3_country` is truthy, so a blank entry would silently return every country's data unfiltered
# and double-count the global total.
all_countries = [c for c in countries_all if c]

frames = []
start_year = 2015
end_year = 2026
# 'edgar', 'ceds', or 'unfccc_crt'
inventory = 'unfccc_crt'

inventory_flags = {
    'edgar': dict(EDGAR=True),
    'ceds': dict(CEDS=True),
    'unfccc_crt': dict(UNFCCC_CRT=True),
}
if inventory not in inventory_flags:
    raise ValueError(f"unknown inventory: {inventory}")
flags = inventory_flags[inventory]

# all countries and years
for a_country in all_countries:
    print("running country:", a_country)
    a_country_instance = CountryPlotting(a_country)
    for a_year in range(start_year, end_year):
        _, output_data = a_country_instance.single_year_comparison_totals(year=a_year, unfccc_year=a_year, lulucf=False, **flags)
        a_df = pd.concat(output_data, names=["source"]).reset_index(level=0).reset_index(drop=True)
        a_df['iso3_country'] = a_country
        frames.append(a_df)

df_all = pd.concat(frames, ignore_index=True)

path = Path(__file__).parent.resolve()
base_folder = "processed_data"
(path / base_folder).mkdir(parents=True, exist_ok=True)

csv_path = path / base_folder / f"global_comparison_{inventory}_by_country_{datetime.date.today()}.csv"
df_all.to_csv(csv_path, index=False)