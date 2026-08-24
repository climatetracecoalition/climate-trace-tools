from subtract_out_plotting import SectorComparison
from climate_trace_tools.compare.country_lists import countries_annex1, countries_nonannex1
from climate_trace_tools.compare.input_helper import InputHelper
import datetime


# get sectors
ih = InputHelper()
available_annex1_sectors = ih.sectors_available_to_plot_subtract_out(annex1=True)
available_not_annex1_sectors = ih.sectors_available_to_plot_subtract_out(annex1=False)
available_sectors = available_annex1_sectors + available_not_annex1_sectors
sectors = list(set(available_sectors))

# get countries
all_countries = countries_annex1 + countries_nonannex1

# set time period
start_year = 2020
end_year = 2023

sc = SectorComparison()

# output_data = sc.plot(countries = all_countries, 
#                              sectors = ['heat-plants'], 
#                              gases = ['all'], 
#                              co2eqs = ['100-year'], 
#                              plot_type=['subsectors'], 
#                              start_year=start_year, 
#                              end_year=end_year, 
#                              name=datetime.date.today(), 
#                              plot_live=False)

output_data = sc.plot(countries = ['JPN'], 
                             sectors = ['road-transportation'], 
                             gases = ['all'], 
                             co2eqs = ['100-year'], 
                             plot_type=['subsectors'], 
                             start_year=start_year, 
                             end_year=end_year, 
                             name=datetime.date.today(), 
                             plot_live=False)