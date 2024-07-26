# Subtract Out Readme

subtract-out has two main capabilities: 

- `SectorComparison` : This class relies on all of the scripts in util, and produces plots based on user input.
- `Helper` : The class has several functions for helping the user to build their inputs for SectorComparison.

Unlike aggregate-up methods, subtract-out is heavily dependent on whether a country is Annex 1 or Non-Annex 1. Because the methodology is based on subtracting out UNFCCC reported data to arrive at comparable answers, annex 1 and non-annex 1 countries will have slightly different results.

## Helper

```python
from helper import InputHelper

ih = InputHelper()
```

### get_available_countries

```python
print(ih.get_available_countries(annex1=True))
```

```python
['AUS', 'AUT', 'BLR', 'BEL', 'BGR', 'CAN', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA', 'DEU', 'GRC', 'HUN', 'ISL', 'IRL', 'ITA', 'JPN', 'KAZ', 'LVA', 'LIE', 'LTU', 'LUX', 'MLT', 'MCO', 'NLD', 'NZL', 'NOR', 'POL', 'PRT', 'ROU', 'RUS', 'SVK', 'SVN', 'ESP', 'SWE', 'CHE', 'TUR', 'UKR', 'GBR', 'USA']
```

### sectors_available_to_plot

```python
print(ih.sectors_available_to_plot(annex1=True))
```

```python
['electricity-generation', 'other-energy-use', 'domestic-aviation', 'international-aviation', 'road-transportation', 'international-shipping', 'domestic-shipping', 'railways', 'other-transport', 'residential-and-commercial-onsite-fuel-usage', 'other-onsite-fuel-usage', 'coal-mining', 'solid-fuel-transformation', 'oil-and-gas-production-and-transport', 'oil-and-gas-refining', 'other-fossil-fuel-operations', 'petrochemicals', 'cement', 'chemicals', 'steel', 'aluminum', 'pulp-and-paper', 'other-manufacturing', 'bauxite-mining', 'iron-mining', 'copper-mining', 'rock-quarrying', 'sand-quarrying', 'enteric-fermentation-cattle-feedlot', 'enteric-fermentation-cattle-pasture', 'enteric-fermentation-other', 'manure-left-on-pasture-cattle', 'manure-management-cattle-feedlot', 'manure-management-other', 'rice-cultivation', 'synthetic-fertilizer-application', 'other-agricultural-soil-emissions', 'cropland-fires', 'solid-waste-disposal', 'biological-treatment-of-solid-waste-and-biogenic', 'incineration-and-open-burning-of-waste', 'wastewater-treatment-and-discharge', 'fluorinated-gases', 'forest-land-fires', 'forest-land-clearing', 'forest-land-degradation', 'net-forest-land', 'net-shrubgrass', 'net-wetland', 'shrubgrass-fires', 'wetland-fires', 'removals', 'water-reservoirs', 'aviation', 'shipping', 'bunker-fuels', 'domestic-transportation', 'fossil-fuel-operations', 'mining-and-quarrying', 'enteric-fermentation', 'enteric-fermentation-cattle', 'manure-management', 'manure-management-cattle', 'energy-industries-and-fugitive-emissions', 'manufacturing-and-industrial-processes', 'transport', 'buildings', 'agriculture', 'waste', 'forestry-and-land-use-change', 'net-forestry-and-land-use-change', 'other-agriculture']
```

### inventories_available_to_compare_for_sector
```python
print(ih.inventories_available_to_compare_for_sector('coal-mining', annex1=True))
```

```python
['climate-trace', 'unfccc_annex_1', 'edgar', 'cait', 'pik-tp']
```

## SectorComparison 

Once SectorComparison is initialized, you only need to run .plot() to get plots for the inputs you’ve selected.

### Inputs

`plot` 

- `countries` : *list.*  iso3 codes for countries you want to plot
- `sectors` : *list.*  sector names for Climate TRACE sectors you want to plot. use helper to get list of sectors available.
- `gases` : *list.* options are *‘ch4’, ‘n2o’, ‘co2’, or ‘all’.* If using plot_type = ‘gases’, gases must be ‘all’.
- `co2eqs` : *list.* options are *'100-year', '20-year', 'both', or 'none'* This will determine the co2 equivalency for the graphs.
    - *'none'* is available for plots showing one gas, this option is skipped when 'all' is specified for `gases`
    - `co2eq` defaults to 'none' for plots showing only 'co2', while ch4 and n2o can take any setting
    - *'both'* shows comparison between 100-year and 20-year estimates on a single plot
- `plot_type` : *list.* options are *‘gases’ or ‘subsectors’*
    - *'subsectors'* shows breakdown by subsector, it is available for every gas and co2eq setting
    - *'gases'* shows a breakdown by each gas's contribution to the total for a sector. It is available for 'all' gases only.
    - *'gases'* setting requires `co2eq` **not** be 'none'
- `start_year` : *int.* start_year for plot.
- `end_year` : *int.* end_year for plot.
- `create_folders` : *bool*. Defaults to False. True will create a system of folders according to your inputs, and store plots in these folders. False will result in the html plot being written to whatever directory you are working in.
- `plot_live` : *bool*. Defaults to True. True will generate html plots in your browser as the code runs. False will not plot the data live, but will save the html plots to your data folder. Helpful to set to False if you are generating a large number of plots.

### Examples

Initializing SectorComparison is the lengthiest part of the process, as it loads in all of the data. If you are working in a jupyter notebook, it is recommended to initialize SectorComparison and then run whatever plots you want on the object. 

```python
from subtract_out_plotting import SectorComparison
sc = SectorComparison()
```

***Subsectors Plot***

```python
sc.plot(countries = ['USA'], sectors = ['electricity-generation'], gases = ['all'], co2eqs = ['100-year'],plot_type=['subsectors'], start_year=2000, end_year=2023, create_folders=False)
```
![newplot - 2024-04-29T195238 778](https://github.com/climatetracecoalition/climate-trace-tools/assets/43048648/098de5c6-36ec-4f53-94fc-2cc2c0b02792)


***Gases Plot***

```python
sc.plot(countries = ['USA'], sectors = ['other-manufacturing'], gases = ['all'], co2eqs = ['100-year'],plot_type=['gases'], start_year=2000, end_year=2023, create_folders=False)
```
![newplot - 2024-04-29T194434 813](https://github.com/climatetracecoalition/climate-trace-tools/assets/43048648/98f24edd-6aa2-421f-9947-28d67fd7b838)

