from subtract_out_plotting import SectorComparison
from helper import InputHelper
import json
from util.country_lists import countries_nonannex1, countries_annex1


ih = InputHelper()

# print(ih.get_available_countries(annex1=True))
# print(ih.sectors_available_to_plot(annex1=True))
# print(ih.inventories_available_to_compare_for_sector('coal-mining', annex1=True))

sc = SectorComparison()
sectors = ['electricity-generation', 'other-energy-use', 'domestic-aviation', 'international-aviation', 'road-transportation', 'international-shipping', 'domestic-shipping', 'railways', 'other-transport', 'residential-and-commercial-onsite-fuel-usage', 'other-onsite-fuel-usage', 'coal-mining', 'solid-fuel-transformation', 'oil-and-gas-production-and-transport', 'oil-and-gas-refining', 'other-fossil-fuel-operations', 'petrochemicals', 'cement', 'chemicals', 'steel', 'aluminum', 'pulp-and-paper', 'other-manufacturing', 'bauxite-mining', 'iron-mining', 'copper-mining', 'rock-quarrying', 'sand-quarrying', 'enteric-fermentation-cattle-feedlot', 'enteric-fermentation-cattle-pasture', 'enteric-fermentation-other', 'manure-left-on-pasture-cattle', 'manure-management-cattle-feedlot', 'manure-management-other', 'rice-cultivation', 'synthetic-fertilizer-application', 'other-agricultural-soil-emissions', 'cropland-fires', 'solid-waste-disposal', 'biological-treatment-of-solid-waste-and-biogenic', 'incineration-and-open-burning-of-waste', 'wastewater-treatment-and-discharge', 'fluorinated-gases', 'forest-land-fires', 'forest-land-clearing', 'forest-land-degradation', 'net-forest-land', 'net-shrubgrass', 'net-wetland', 'shrubgrass-fires', 'wetland-fires', 'removals', 'water-reservoirs', 'aviation', 'shipping', 'bunker-fuels', 'domestic-transportation', 'fossil-fuel-operations', 'mining-and-quarrying', 'enteric-fermentation', 'enteric-fermentation-cattle', 'manure-management', 'manure-management-cattle', 'energy-industries-and-fugitive-emissions', 'manufacturing-and-industrial-processes', 'transport', 'buildings', 'agriculture', 'waste', 'forestry-and-land-use-change', 'net-forestry-and-land-use-change', 'other-agriculture']

# sectors = ['domestic-aviation']

countries_annex1 = ['USA']
sectors = ['other-manufacturing']

sc.plot(countries = countries_annex1, sectors = sectors, gases = ['all'], co2eqs = ['100-year'],plot_type=['gases'], start_year=2000, end_year=2023)