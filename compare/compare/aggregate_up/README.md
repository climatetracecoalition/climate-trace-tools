# Aggregate Up Readme

### Single Year Comparison Totals

INPUT:

```jsx
from aggregate_up_plotting import CountryPlotting

cp_usa = CountryPlotting('USA')
cp_usa.single_year_comparison_totals(year=2021, unfccc_year=2021, UNFCCC=True, EDGAR=True, lulucf=False)
```

### Single Year Comparison Sectors

INPUT:

```jsx
from aggregate_up_plotting import CountryPlotting

cp_chn = CountryPlotting('CHN')
fig, output_data = cp_chn.single_year_comparison_sectors('co2e_100yr', year=2022, EDGAR=True, lulucf=False)
```

### Single Year Comparison Subsectors

INPUT:

```jsx
from aggregate_up_util import get_subsector_options

subsectors = get_subsector_options('cait')
print(subsectors)
```

OUTPUT:

```jsx
['Agriculture', 'Buildings', 'Energy Industries and Fugitive Emissions', 'Forestry and Land Use Change', 'Manufacturing and Industrial Processes', 'Transport', 'Waste']
```

INPUT:
```jsx
from aggregate_up_plotting import CountryPlotting

cp_esp = CountryPlotting('ESP')
fig, output_data = cp_esp.single_year_comparison_subsectors('co2e_100yr', year=2020, sector='Energy Industries and Fugitive Emissions',CAIT=True)
```
INPUT:

```jsx
from aggregate_up_plotting import CountryPlotting

#sector is False 

cp_esp = CountryPlotting('ESP')
fig, output_data = cp_esp.single_year_comparison_subsectors('co2e_100yr', year=2020, sector=False,CAIT=True)
```

### Single Year Comparison Subsector Gases

```jsx
from aggregate_up_plotting import CountryPlotting

cp_rus = CountryPlotting('RUS')
print(cp_rus.get_latest_year_for_inventory(UNFCCC=True))
```

```jsx
2021-01-01 00:00:00
```

```jsx
from aggregate_up_util import get_subsector_options

print(get_subsector_options('unfccc_annex_1'))
```

```python
[['Cropland Fires', 'Enteric Fermentation (Cattle)', 'Enteric Fermentation (Other)', 'Manure Management (Cattle)', 'Manure Management (Other)', 'Other Agricultural Soil Emissions', 'Other Agriculture', 'Rice Cultivation', 'Synthetic Fertilizer Application'], ['Other Onsite Fuel Usage', 'Residential and Commercial Onsite Fuel Usage'], ['Coal Mining', 'Electricity Generation', 'Oil and Gas Production and Transport', 'Oil and Gas Refining', 'Other Energy Use', 'Other Fossil Fuel Operations', 'Solid Fuel Transformation'], ['Net Forest Land', 'Net Shrubgrasss', 'Net Wetland', 'Water Reservoirs'], ['Aluminum', 'Cement', 'Chemicals', 'Fluorinated Gases', 'Mining and Quarrying', 'Other Manufacturing', 'Petrochemicals', 'Pulp and Paper', 'Steel'], ['Domestic Aviation', 'Domestic Shipping', 'International Aviation', 'International Shipping', 'Other Transport', 'Railways', 'Road Transportation'], ['Biological Treatment of Solid Waste', 'Incineration and Open Burning of Waste', 'Other Waste', 'Solid Waste Disposal', 'Wastewater Treatment and Discharge']]

```

```jsx
from aggregate_up_plotting import CountryPlotting

cp_rus = CountryPlotting('RUS')

fig, output_data = cp_rus.single_year_comparison_subsector_gases(year=2021, subsector='Oil and Gas Production and Transport',UNFCCC=True)
```

### Single Inventory All Sectors Across Years

```python
from aggregate_up_plotting import CountryPlotting

cp_bra = CountryPlotting('BRA')
fig, output_data = cp_bra.single_inventory_all_sectors_across_years(years=[2015,2016,2017,2018,2019,2020,2021], ClimateTRACE=True)
```

### Single Inventory Single Sector Across Years

```python
from aggregate_up_plotting import CountryPlotting

print(get_sector_options('carbon-monitor'))
```

```python
['Domestic Aviation', 'Electricity Generation', 'International Aviation', 'Manufacturing and Industrial Processes', 'Residential and Commercial Onsite Fuel Usage', 'Road Transportation']
```

```python
from aggregate_up_plotting import CountryPlotting

cp_fra = CountryPlotting('FRA')
cp_fra.single_inventory_all_sectors_across_years(years=[2015,2016,2017,2018,2019,2020,2021], sector = 'Electricity Generation', CarbonMonitor=True)
```

```python
from aggregate_up_plotting import CountryPlotting

cp_fra = CountryPlotting('FRA')
cp_fra.single_inventory_single_sector_across_years(years=[2015,2016,2017,2018,2019,2020,2021], sector = 'Energy Industries and Fugitive Emissions', UNFCCC=True)
```
