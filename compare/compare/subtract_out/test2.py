from main import SectorComparison
from helper import InputHelper
import json


# ih = InputHelper()
#
# print(ih.sectors_available_to_plot(annex1=False))
# print(ih.inventories_available_to_compare_for_sector('coal-mining', annex1=False))

sc = SectorComparison()

sc.process_all(countries = ['CHN'], sectors = ['coal-mining', 'electricity-generation'], gases = ['ch4'], co2eqs = ['100-year'],plot_type=['subsectors'], start_year=2000, end_year=2023)