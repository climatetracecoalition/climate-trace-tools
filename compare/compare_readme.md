# Compare Readme

A common problem with emissions data is that not all inventories are measuring the exact same set of emissions, and everybody defines “sector” a little bit differently. In order to validate our data, Climate TRACE has set out to build tools that make data comparable. 

We decided to anchor the comparisons around the [2019 IPCC reporting categories](https://www.ipcc-nggip.iges.or.jp/public/2019rf/index.html), as it is the most comprehensive and granular categorization of emissions sources. The first step of making inventories comparable is to assign an IPCC code to the sector from a given datasource. This information is stored in `sector_coverage` . 

Once we have assigned an IPCC code to the sector, we have two techniques for attempting to make the data comparable when the sector definitions do not match exactly:

*Note: Currently, we have only created tools for comparison at the country or global level. When we import source level estimates from other sources, we assign IPCC codes to those sectors and map them to Climate TRACE sectors. We are working on developing tools for comparability across source level emissions.* 

- Aggregate up: If two inventories define a sector slightly differently, we can aggregate sectors into larger groupings in order for the codes contained in each to match closely. For example, Climate TRACE currently groups emissions information by industry and has not split them out into 1.A (Energy use) and 1.B (Fugitive Emissions) for `oil-and-gas-production-and-transport` or `oil-and-gas-refining`. EDGAR, however, does split estimates into 1.A and 1.B. In order to compare our estimates for these sectors, we add together all of the sectors that measure emissions in either 1.A or 1.B together into a comparison sector called “Energy Industries and Fugitive Emissions”. In some cases, depending on the comparison inventory, we can aggregate to a comparison subsector as well.
    - The graph below shows an example of the output of this type of comparison.
![aggregate_up_example](https://github.com/climatetracecoalition/climate-trace-tools/assets/43048648/5108392c-ced8-408f-a11a-ee316a956bef)


 

- Subtract Out: This method relies on country self-reported data to the UNFCCC and also mixes and matches different inventories to attempt to isolate a specific Climate TRACE sector for comparison. It is slightly less reliable than *aggregate up*, but can give insightful clues about how sectors compare. In the example plot below, we are comparing Climate TRACE’s electricity-generation sector to other inventories. The PIK inventory measures all emissions in 1.A, whereas Climate TRACE electricity generation is only measuring 1.A.1.a.  The following two graphs illustrate how we might make these comparable, for an annex 1 country as well as a non annex 1 country.
    - Annex 1: Because Canada reports at a high level of granularity, we can subtract out all of the sectors that they report within 1.A that are not 1.A.1.a. The dotted purple line shows PIK’s original estimate for 1.A. The solid purple line shows the “subtracted out” estimate for 1.A.1.a. We can see that it is now within the range of the other estimates for 1.A.1.a from EDGAR, UNFCCC, and Climate TRACE.
![subtract_out_electricity_canada](https://github.com/climatetracecoalition/climate-trace-tools/assets/43048648/823ae617-7603-47ff-949d-905d592966aa)



- Non Annex 1:
    - Argentina: Because Argentina is a non-annex 1 country, they do not report at a high enough granularity to make the data exactly comparable. The dotted purple line shows PIK’s original estimate for 1.A. Argentina’s report to the UNFCCC contains data down to the 1.A.1 level, so we subtract out 1.A.2, 1.A.3, and 1.A.4 to attempt to isolate 1.A.1. The subtraction only occurs for the years that Argentina has reported, so the solid purple line will be spiky. The purple line should now theoretically match UNFCCC estimates since 1.A.1. has been isolated. However, we can see that PIK’s estimates are slightly higher.
![subtract_out_electricity_argentina](https://github.com/climatetracecoalition/climate-trace-tools/assets/43048648/19ec4180-7222-482a-b928-8470ef3f7497)

    - Saudi Arabia: Saudi Arabia is also a non-annex 1 country and reports only down to the 1.A.1 level. Though we cannot make the comparisons exactly equal, we can walk through what we can still glean from this comparison. The solid purple line shows the inferred PIK estimate for 1.A.1, and we can see that it is significantly higher than the what Saudi Arabia self reported to the UNFCCC (orange diamonds). We also see that the UNFCCC estimates match EDGAR almost exactly, but that shouldn’t be the case. EDGAR is measuring only 1.A.1.a, and UNFCC is measuring 1.A.1. This would imply that Saudi Arabia, one of the world’s biggest oil producers has no energy use emissions associated with Petroleum refining (1.A.1.b). Though this graph doesn’t give us exact answers, it gives a clue on where countries might be underreporting.
 ![subtract_out_electricity_saudi_arabia](https://github.com/climatetracecoalition/climate-trace-tools/assets/43048648/460b57fe-1403-40e8-af1e-78d6caeaf751)

