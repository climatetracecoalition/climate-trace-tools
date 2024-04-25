

from aggregate_up_util import get_subsector_options, get_sector_options
from aggregate_up_plotting import CountryPlotting


from aggregate_up_plotting import CountryPlotting



cp_fra = CountryPlotting('FRA')
cp_fra.single_inventory_single_sector_across_years(years=[2015,2016,2017,2018,2019,2020,2021], sector = 'Energy Industries and Fugitive Emissions', UNFCCC=True)

# print(output_data)

print(get_sector_options('unfccc_annex_1'))


# cp_usa = CountryPlotting('USA')
#
# cp_usa.single_year_comparison_totals(year=2021, unfccc_year=2021, UNFCCC=True, EDGAR=True, lulucf=False)
