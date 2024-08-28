"""This script builds 4 dictionaries that the SectorComparison class rely on.

The 4 dictionaries that will be written from running this script are:
- master_comparison_dict_annex1.json
- master_comparison_dict_nonannex1.json
- title_dict_annex1.json
- title_dict_nonannex1.json

The script requires a xlsx input, which is stored in the /files directory. This xlsx file contains
mappings upon which the subtract out code runs.
"""

import pandas as pd
import json

# Specify the path to the XLSX file with the comparison dictionaries.
#
# and then put it in the files directory within this directory
xlsx_file_path = "files/subtract-out-csv-crosswalks.xlsx"
# Define the list of tabs in your XLSX (assuming each tab corresponds to a separate sheet)
tabs = [
    "climate-trace-subtract-out",
    "unfccc-subtract-out",
    "ceds-subtract-out",
    "carbon-monitor-subtract-out",
    "edgar-subtract-out",
    "cait-subtract-out",
    "pik-tp-subtract-out",
    "faostat-subtract-out",
]

inventory_titles = {
    "climate-trace": "ClimateTRACE",
    "unfccc_annex_1": "UNFCCC",
    "unfccc_non_annex_1": "UNFCCC",
    "edgar": "EDGAR",
    "cait": "CAIT",
    "pik-tp": "PIK",
    "ceds": "CEDS",
    "carbon-monitor": "Carbon Monitor",
    "faostat": "FAOSTAT",
}

inventory_codes = {
    "unfccc-subtract-out": "unfccc",
    "carbon-monitor-subtract-out": "carbon-monitor",
    "edgar-subtract-out": "edgar",
    "cait-subtract-out": "cait",
    "ceds-subtract-out": "ceds",
    "pik-tp-subtract-out": "pik-tp",
    "faostat-subtract-out": "faostat",
    "climate-trace-subtract-out": "climate-trace",
}


def create_sector_title(raw_string):
    formatted_string = raw_string.replace("-", " ")

    # Capitalize words in the title
    formatted_string = formatted_string.title()

    return formatted_string


def get_inventory_name(tab_name, annex_1):
    names = inventory_codes
    if annex_1:
        names["unfccc-subtract-out"] = "unfccc_annex_1"
    else:
        names["unfccc-subtract-out"] = "unfccc_non_annex_1"

    return names[tab_name]


def generate_master_dicts():
    # Initialize JSON objects for Annex 1 and Non-Annex 1 data
    annex1_data = {}
    non_annex1_data = {}

    for tab_name in tabs:
        # Read the XLSX file for the current tab
        df = pd.read_excel(xlsx_file_path, sheet_name=tab_name)
        df = df.dropna()

        for index, row in df.iterrows():
            annex_1 = row["Annex 1?"]
            climate_trace_sector = row["Climate TRACE Sector"]
            inventory = row["Inventory"]
            sector = row["Sector"]
            value = int(row["Value"])
            inventory_code = get_inventory_name(tab_name, annex_1)
            if sector != "NaN":
                if annex_1:
                    if climate_trace_sector not in annex1_data:
                        annex1_data[climate_trace_sector] = {}
                    if inventory_code not in annex1_data[climate_trace_sector]:
                        annex1_data[climate_trace_sector][inventory_code] = {}
                    if (
                        inventory
                        not in annex1_data[climate_trace_sector][inventory_code]
                    ):
                        annex1_data[climate_trace_sector][inventory_code][
                            inventory
                        ] = []
                    if (
                        (climate_trace_sector == "electricity-generation")
                        & (inventory_code == "pik-tp")
                        & (inventory == "pik-tp")
                    ):
                        annex1_data[climate_trace_sector][inventory_code][
                            inventory
                        ].append(("1", value))
                    else:
                        annex1_data[climate_trace_sector][inventory_code][
                            inventory
                        ].append((sector, value))
                else:
                    if climate_trace_sector not in non_annex1_data:
                        non_annex1_data[climate_trace_sector] = {}
                    if inventory_code not in non_annex1_data[climate_trace_sector]:
                        non_annex1_data[climate_trace_sector][inventory_code] = {}
                    if (
                        inventory
                        not in non_annex1_data[climate_trace_sector][inventory_code]
                    ):
                        non_annex1_data[climate_trace_sector][inventory_code][
                            inventory
                        ] = []
                    if (
                        (climate_trace_sector == "electricity-generation")
                        & (inventory_code == "pik-tp")
                        & (inventory == "pik-tp")
                    ):
                        non_annex1_data[climate_trace_sector][inventory_code][
                            inventory
                        ].append(("1", value))
                    else:
                        non_annex1_data[climate_trace_sector][inventory_code][
                            inventory
                        ].append((sector, value))

    # Convert the dictionaries to JSON
    # Print or save the JSON objects as needed
    # annex1_data["electricity-generation"]["pik-tp"]["pik-tp"][0][0] = "1"
    # non_annex1_data["electricity-generation"]["pik-tp"]["pik-tp"][0][0] = "1"
    with open("files/master_comparison_dict_annex1.json", "w") as f:
        f.write(json.dumps(annex1_data, indent=2))

    with open("files/master_comparison_dict_nonannex1.json", "w") as f:
        f.write(json.dumps(non_annex1_data, indent=2))


def generate_title_dicts():
    # Initialize JSON objects for Annex 1 and Non-Annex 1 data
    annex1_data = {}
    non_annex1_data = {}

    for tab_name in tabs:
        # Read the XLSX file for the current tab
        df = pd.read_excel(xlsx_file_path, sheet_name=tab_name)
        df = df.dropna()

        for index, row in df.iterrows():
            annex_1 = row["Annex 1?"]
            climate_trace_sector = row["Climate TRACE Sector"]
            inventory = row["Inventory"]
            inventory_title = inventory_titles[inventory]
            sector = row["Sector"]
            sector_title = create_sector_title(climate_trace_sector)
            value = int(row["Value"])
            inventory_name = get_inventory_name(tab_name, annex_1)

            if value > 0:
                value_string = "     + "
            else:
                value_string = "     - "
            if sector != "NaN":
                if annex_1:
                    if climate_trace_sector not in annex1_data:
                        annex1_data[climate_trace_sector] = {
                            "title": sector_title,
                            "legend": {},
                        }

                    # if tab_name not in annex1_data[climate_trace_sector]['legend']:
                    #

                    if (
                        inventory_name
                        not in annex1_data[climate_trace_sector]["legend"]
                    ):
                        annex1_data[climate_trace_sector]["legend"][inventory_name] = {}
                    if (
                        inventory
                        not in annex1_data[climate_trace_sector]["legend"][
                            inventory_name
                        ]
                    ):
                        annex1_data[climate_trace_sector]["legend"][inventory_name][
                            inventory
                        ] = {"desc": inventory_title, "comps": []}
                    if (
                        (climate_trace_sector == "electricity-generation")
                        & (inventory_name == "pik-tp")
                        & (inventory == "pik-tp")
                    ):
                        annex1_data[climate_trace_sector]["legend"][inventory_name][
                            inventory
                        ]["comps"].append(("1", value_string))
                    else:
                        annex1_data[climate_trace_sector]["legend"][inventory_name][
                            inventory
                        ]["comps"].append((sector, value_string))
                else:
                    if climate_trace_sector not in non_annex1_data:
                        non_annex1_data[climate_trace_sector] = {
                            "title": sector_title,
                            "legend": {},
                        }

                    if (
                        inventory_name
                        not in non_annex1_data[climate_trace_sector]["legend"]
                    ):
                        non_annex1_data[climate_trace_sector]["legend"][
                            inventory_name
                        ] = {}
                    if (
                        inventory
                        not in non_annex1_data[climate_trace_sector]["legend"][
                            inventory_name
                        ]
                    ):
                        non_annex1_data[climate_trace_sector]["legend"][inventory_name][
                            inventory
                        ] = {"desc": inventory_title, "comps": []}
                    if (
                        (climate_trace_sector == "electricity-generation")
                        & (inventory_name == "pik-tp")
                        & (inventory == "pik-tp")
                    ):
                        non_annex1_data[climate_trace_sector]["legend"][inventory_name][
                            inventory
                        ]["comps"].append(("1", value_string))
                    else:
                        non_annex1_data[climate_trace_sector]["legend"][inventory_name][
                            inventory
                        ]["comps"].append((sector, value_string))

    # Convert the dictionaries to JSON
    # Print or save the JSON objects as needed

    with open("files/title_dict_annex1.json", "w") as f:
        f.write(json.dumps(annex1_data, indent=2))

    with open("files/title_dict_nonannex1.json", "w") as f:
        f.write(json.dumps(non_annex1_data, indent=2))


if __name__ == "__main__":
    generate_master_dicts()
    generate_title_dicts()
