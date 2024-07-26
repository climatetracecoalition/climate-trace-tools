# Aggregate Up Readme

### Single Year Comparison Totals

INPUT:

```jsx
from aggregate_up_plotting import CountryPlotting

cp_usa = CountryPlotting('USA')
cp_usa.single_year_comparison_totals(year=2021, unfccc_year=2021, UNFCCC=True, EDGAR=True, lulucf=False)
```

OUTPUT:
![newplot - 2024-04-22T161923 589](https://github.com/climatetracecoalition/climate-trace-tools/assets/43048648/3712ee61-a64e-4dec-aafa-da44a1415681)


### Single Year Comparison Sectors

INPUT:

```jsx
from aggregate_up_plotting import CountryPlotting

cp_chn = CountryPlotting('CHN')
fig, output_data = cp_chn.single_year_comparison_sectors('co2e_100yr', year=2022, EDGAR=True, lulucf=False)
```

OUTPUT: 
![single_year_comparison_sectors](https://github.com/climatetracecoalition/climate-trace-tools/assets/43048648/76b65c92-d76a-4643-a224-4109e897b549)

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

OUTPUT:
![single_year_comparison_subsectors](https://github.com/climatetracecoalition/climate-trace-tools/assets/43048648/21fbd5bb-f57f-403e-80d4-7bdcd0496090)


INPUT:

```jsx
from aggregate_up_plotting import CountryPlotting

#sector is False 

cp_esp = CountryPlotting('ESP')
fig, output_data = cp_esp.single_year_comparison_subsectors('co2e_100yr', year=2020, sector=False,CAIT=True)
```

OUTPUT:
![single_year_comparison_subsectors2](https://github.com/climatetracecoalition/climate-trace-tools/assets/43048648/4654ef5e-824b-4c3c-af78-b136b120b347)



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
INPUT: 

```jsx
from aggregate_up_plotting import CountryPlotting

cp_rus = CountryPlotting('RUS')

fig, output_data = cp_rus.single_year_comparison_subsector_gases(year=2021, subsector='Oil and Gas Production and Transport',UNFCCC=True)
```

OUTPUT: 

![single_year_comparison_gases](https://github.com/climatetracecoalition/climate-trace-tools/assets/43048648/5ec9b4eb-6c27-4d76-8db5-b3f27c14fe2f)

### Single Inventory All Sectors Across Years

INPUT:

```python
from aggregate_up_plotting import CountryPlotting

cp_bra = CountryPlotting('BRA')
fig, output_data = cp_bra.single_inventory_all_sectors_across_years(years=[2015,2016,2017,2018,2019,2020,2021], ClimateTRACE=True)
```

OUTPUT: 
![single_inventory_across_years](https://github.com/climatetracecoalition/climate-trace-tools/assets/43048648/cb3f2292-7770-4f6d-8378-a0e94c4cb366)


### Single Inventory Single Sector Across Years

```python
from aggregate_up_plotting import CountryPlotting

print(get_sector_options('carbon-monitor'))
```

```python
['Domestic Aviation', 'Electricity Generation', 'International Aviation', 'Manufacturing and Industrial Processes', 'Residential and Commercial Onsite Fuel Usage', 'Road Transportation']
```
INPUT:

```python
from aggregate_up_plotting import CountryPlotting

cp_fra = CountryPlotting('FRA')
cp_fra.single_inventory_all_sectors_across_years(years=[2015,2016,2017,2018,2019,2020,2021], sector = 'Electricity Generation', CarbonMonitor=True)
```

OUTPUT: 
![ single_inventory_single_sector](https://github.com/climatetracecoalition/climate-trace-tools/assets/43048648/986da129-7098-4e3d-a445-5dd2f9483f9e)


INPUT: 
```python
from aggregate_up_plotting import CountryPlotting

cp_fra = CountryPlotting('FRA')
cp_fra.single_inventory_single_sector_across_years(years=[2015,2016,2017,2018,2019,2020,2021], sector = 'Energy Industries and Fugitive Emissions', UNFCCC=True)
```

OUTPUT: 

![single_inventory_single_sector2](https://github.com/climatetracecoalition/climate-trace-tools/assets/43048648/c03a6626-109a-4966-a611-351c11df6c6d)
