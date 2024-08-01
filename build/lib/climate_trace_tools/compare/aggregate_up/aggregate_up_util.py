import json


def parent_sector_map(country, datasource, datasourcedf, sector_dict):
    """
    ∂Function creates parent sectors column for UNFCCC and EDGAR data, mapping from plotting_dict,
     to match up with CT sectors in plotting functions.
    """

    sector_map = {}

    for x in sector_dict.keys():
        key_sectors = sector_dict.get(x, {}).get(datasource)
        if key_sectors:
            for i in key_sectors:
                sector_map.update({i: x})

    data_sub = datasourcedf.copy()
    data_sub["parent_sector"] = data_sub["original_inventory_sector"].map(sector_map)
    if country:
        data_sub = data_sub.loc[(data_sub["iso3_country"] == country)].copy()
    # data_sub = data_sub.loc[(data_sub['parent_sector'].notnull()) &\
    #                             (data_sub['iso3_country'] == country)].copy()
    data_sub["year"] = data_sub["start_time"].dt.year

    return data_sub


def subsector_map(parent_sector, datasource, datasourcedf, plotting_dict):
    """
    Function creates subsector column for Climate TRACE and EDGAR data, mapping from plotting_dict
    """
    subsector_map = {}
    #
    if parent_sector:
        sector_dict = plotting_dict.get(parent_sector)
        for x in sector_dict.keys():
            key_subsectors = sector_dict.get(x, {}).get(datasource)
            for i in key_subsectors:
                subsector_map.update({i: x})
    else:
        for sector, sector_dict in plotting_dict.items():
            for x in sector_dict.keys():
                key_subsectors = sector_dict.get(x, {}).get(datasource)
                for i in key_subsectors:
                    subsector_map.update({i: x})

    data_sub = datasourcedf.copy()
    data_sub["subsector"] = data_sub["original_inventory_sector"].map(subsector_map)

    return data_sub


def sector_color_map():
    color_dict = {
        "Energy Industries and Fugitive Emissions": "darkgreen",
        # 'Energy Industries and Fugitive Emissions': '#1A1A1A',
        "Energy Industries, Fugitive Emissions, Buildings, and Transport": "#1A1A1A",  # green
        "Manufacturing and Industrial Processes": "#110C45",  # dark blue
        "Transport": "#1F2C69",  # light blue
        "Buildings": "yellow",
        # 'Buildings': '#325697', # light gray
        "Agriculture": "#3E8AB5",  # black
        "Forestry and Land Use Change": "#4BC1D5",  # lighter blue than dark but not as light as light
        "Waste": "#50D7E2",
        "Other": "white",
    }

    return color_dict


def subsector_color_map():
    color_dict = {
        "Agriculture": {
            "Agriculture": "red",
            "Enteric Fermentation (Cattle)": "gold",
            "Enteric Fermentation (Other)": "goldenrod",
            "Manure Management (Cattle)": "mediumseagreen",
            "Manure Management (Cattle)": "forestgreen",
            "Rice Cultivation": "firebrick",
            "Synthetic Fertilizer Application": "mediumpurple",
            "Cropland Fires": "darkorange",
            "Other Agriculture": "lightskyblue",
            "Other Agricultural Soil Emissions": "gray",
            "Livestock": "gold",
            "Agriculture Excluding Livestock": "darkorange",
        },
        "Energy Industries, Fugitive Emissions, Buildings, and Transport": {
            "Energy Industries, Buildings, and Domestic Transportation": "midnightblue",
            "International Transportation": "crimson",
            "Fossil Fuel Operations": "darkorange",
            "Coal Mining and Solid Fuel Transformation": "darkgray",
            "Oil and Gas Production and Transport": "darkmagenta",
            "Other Fossil Fuel Operations": "darkkhaki",
        },
        "Energy Industries and Fugitive Emissions": {
            "Electricity Generation and Other Energy Use": "midnightblue",
            "Fossil Fuel Operations": "darkorange",
            "Energy Industries": "blue",
            "Electricity Generation": "midnightblue",
            "Other Energy Use": "crimson",
            "Coal Mining": "darkgray",
            "Solid Fuel Transformation": "darkgreen",
            "Oil and Gas Production and Transport": "darkmagenta",
            "Oil and Gas Refining": "darkseagreen",
            "Other Fossil Fuel Operations": "darkkhaki",
        },
        "Manufacturing and Industrial Processes": {
            "Manufacturing and Industrial Processes": "black",
            "Other Manufacturing  and Industrial Processes": "black",
            "Cement": "midnightblue",
            "Petrochemicals": "firebrick",
            "Chemicals": "mediumseagreen",
            "Metal Industry": "crimson",
            "Steel": "mediumpurple",
            "Aluminum": "grey",
            "Pulp and Paper": "goldenrod",
            "Other Manufacturing": "black",
            "Mining and Quarrying": "darkviolet",
            "Fluorinated Gases": "pink",
        },
        "Transport": {
            "Aviation": "darkgrey",
            "Domestic Aviation": "lightgrey",
            "International Aviation": "darkgrey",
            "Road Transportation": "firebrick",
            "Railways": "mediumseagreen",
            "Water Navigation": "cornflowerblue",
            "International Shipping": "cornflowerblue",
            "Domestic Shipping": "crimson",
            "Other Transport": "plum",
            "Bunker Fuels": "firebrick",
            "Domestic Transportation": "crimson",
        },
        "Buildings": {
            "Residential and Commercial Onsite Fuel Usage": "lightcoral",
            "Other Onsite Fuel Usage": "lightblue",
            "Buildings": "lightblue",
        },
        "Waste": {
            "Biological Treatment of Solid Waste": "grey",
            "Incineration and Open Burning of Waste": "blue",
            "Wastewater Treatment and Discharge": "green",
            "Solid Waste Disposal and Wastewater Treatment": "green",
            "Other Waste": "yellow",
            "Waste": "yellow",
        },
        "Forestry and Land Use Change": {
            "Net Forest Land": "forestgreen",
            "Net Shrubgrass": "goldenrod",
            "Net Wetland": "cornflowerblue",
            "Water Reservoirs": "darkcyan",
            "Other": "darkcyan",
        },
    }

    return color_dict


def inventory_color_map():
    color_dict = {
        "climate-trace": "#50d7e2",  # electric blue
        "edgar": "#110c45",  # dark blue
        "unfccc_annex_1": "darkgray",
        "unfccc_non_annex_1": "darkgray",
        "pik-tp": "goldenrod",
        "cait": "darkmagenta",
    }

    return color_dict


def gas_color_map():
    color_dict = {"co2": "cornflowerblue", "n2o": "darkmagenta", "ch4": "tomato"}
    return color_dict


def fires_sector_dictionary():
    fires_dict = {
        "Fires": {
            "climate-trace": [
                "cropland-fires",
                "forest-land-fires",
                "shrubgrass-fires",
                "wetland-fires",
            ],
            "edgar": ["3.C.1 Emissions from biomass burning"],
        }
    }
    return fires_dict


def get_tick_label_dict():
    tick_label_dict = {
        "climate-trace": "Climate TRACE",
        "unfccc_annex_1": "UNFCCC Annex 1",
        "unfccc_non_annex_1": "UNFCCC Non-Annex 1",
        "edgar": "Edgar",
        "cait": "CAIT",
        "pik-tp": "PIK-TP",
        "gcp": "GCP",
        "carbon-monitor": "Carbon Monitor",
    }
    return tick_label_dict


def plotly_formatting():
    fonts = {"family": "Foros, medium", "color": "Black"}

    layout = {
        "paper_bgcolor": "rgba(255, 255, 255)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "title": f"Comparing emissions estimates from ClimateTRACE 2023 release vs. Climate TRACE 2022 release",
        "title_font": {"size": 25},
        "title_y": 0.9,
        "font": fonts,
        "legend": {
            "traceorder": "normal",
            "groupclick": "toggleitem",
            "x": 1.05,
        },
        "margin": {"l": 100, "r": 100, "t": 120, "b": 80},
    }

    yaxes = {
        "gridcolor": "#e6f3ff",
        "linewidth": 1,
        "ticks": "outside",
        "tickcolor": "#e6f3ff",
        "tickwidth": 1,
        "ticklen": 20,
        "zeroline": True,
        "zerolinewidth": 1,
        "zerolinecolor": "#e6f3ff",
        "showline": True,
        "linecolor": "#e6f3ff",
        "title": "tonnes CO2e",
        "tickfont": {"size": 13},
    }

    xaxes = {"gridcolor": "#e6f3ff", "linewidth": 1, "tickfont": {"size": 13}}

    return fonts, layout, yaxes, xaxes
