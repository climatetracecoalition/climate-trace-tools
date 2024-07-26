import pandas as pd
import json

# Specify the path to the XLSX file with the comparison dictionaries.
# and then put it in the spreadsheets directory within this directory

xlsx_file_path = "files/aggregate-up-csv-crosswalks.xlsx"

# Define the list of tabs in your XLSX (assuming each tab corresponds to a separate sheet)
tabs = [
    "unfccc-aggregate-up",
    "edgar-aggregate-up",
    "cait-aggregate-up",
    "pik-tp-aggregate-up",
    "faostat-aggregate-up",
    "carbon-monitor-aggregate-up",
    "gcp-aggregate-up",
]

inventory_titles = {
    "unfccc-aggregate-up": "unfccc",
    "edgar-aggregate-up": "edgar",
    "cait-aggregate-up": "cait",
    "pik-tp-aggregate-up": "pik-tp",
    "faostat-aggregate-up": "faostat",
    "carbon-monitor-aggregate-up": "carbon-monitor",
    "gcp-aggregate-up": "gcp",
}


def get_sector_list(raw_list):
    return raw_list.split(", ")


def generate_sector_comparison_dict():
    # Initialize JSON objects for Annex 1 and Non-Annex 1 data
    sector_map = {}

    for tab_name in tabs:
        if tab_name in [
            "pik-tp-aggregate-up",
            "carbon-monitor-aggregate-up",
            "gcp-aggregate-up",
        ]:
            continue
        # Read the XLSX file for the current tab
        df = pd.read_excel(xlsx_file_path, sheet_name=tab_name)

        comp_sectors = df["Comparison Sector"].unique().tolist()

        for comp_sector in comp_sectors:

            if comp_sector not in sector_map:
                sector_map[comp_sector] = {}
            filtered_df = df[df["Comparison Sector"] == comp_sector]
            if tab_name == "unfccc-aggregate-up":
                filtered_df = filtered_df[filtered_df["Comparison Subsector"].isna()]

            ct_sectors = []
            inv_sectors = []
            if tab_name == "unfccc-aggregate-up":
                inv_2_sectors = []

            for index, row in filtered_df.iterrows():
                if pd.notna(row[2]):
                    ct_sectors = ct_sectors + get_sector_list(row[2])
                if pd.notna(row[3]):
                    inv_sectors = inv_sectors + get_sector_list(row[3])
                if tab_name == "unfccc-aggregate-up":
                    if pd.notna(row[4]):
                        inv_2_sectors = inv_2_sectors + get_sector_list(row[4])

            if "climate-trace" not in sector_map[comp_sector] and len(ct_sectors) > 0:
                sector_map[comp_sector]["climate-trace"] = ct_sectors
            if tab_name == "unfccc-aggregate-up":
                if len(inv_sectors) > 0:
                    sector_map[comp_sector]["unfccc_annex_1"] = inv_sectors
                if len(inv_2_sectors) > 0:
                    sector_map[comp_sector]["unfccc_non_annex_1"] = inv_2_sectors
            else:
                if len(inv_sectors) > 0:
                    sector_map[comp_sector][inventory_titles[tab_name]] = inv_sectors

    # isolate fires from main comparison dictionary
    fires = {}
    fires["Fires"] = sector_map["Fires"]

    # write fires dictionary separately
    with open("files/comparison_sector_dictionary_fires.json", "w") as f:
        f.write(json.dumps(fires, indent=2))

    sector_map.pop("Fires")
    # Print or save the JSON objects as needed
    with open("files/comparison_sector_dictionary.json", "w") as f:
        f.write(json.dumps(sector_map, indent=2))


def generate_inventory_specific_sector_comparison_dicts(tab_name):
    sector_map = {}

    # Read the XLSX file for the current tab
    df = pd.read_excel(xlsx_file_path, sheet_name=tab_name)
    title = inventory_titles[tab_name]
    comp_sectors = df["Comparison Sector"].unique().tolist()

    for comp_sector in comp_sectors:
        if comp_sector not in sector_map:
            sector_map[comp_sector] = {}
        filtered_df = df[df["Comparison Sector"] == comp_sector]

        ct_sectors = []
        inv_sectors = []

        for index, row in filtered_df.iterrows():
            if pd.notna(row[2]):
                ct_sectors = ct_sectors + get_sector_list(row[2])
            if pd.notna(row[3]):
                if comp_sector in ["Waste", "Other"]:
                    inv_sectors = inv_sectors + [str(row[3])]
                else:
                    inv_sectors = inv_sectors + get_sector_list(row[3])

        if "climate-trace" not in sector_map[comp_sector] and len(ct_sectors) > 0:
            sector_map[comp_sector]["climate-trace"] = ct_sectors

        if len(inv_sectors) > 0:
            sector_map[comp_sector][inventory_titles[tab_name]] = inv_sectors

    # Print or save the JSON objects as needed
    with open(f"files/comparison_sector_dictionary_{title}.json", "w") as f:
        f.write(json.dumps(sector_map, indent=2))


def generate_subsector_comparison_dict(tab_name):
    # Initialize JSON objects for Annex 1 and Non-Annex 1 data
    subsector_map = {}
    # Read the XLSX file for the current tab
    df = pd.read_excel(xlsx_file_path, sheet_name=tab_name)

    comp_sectors = df["Comparison Sector"].unique().tolist()

    for comp_sector in comp_sectors:
        if comp_sector not in subsector_map:
            subsector_map[comp_sector] = {}
        sector_df = df[
            (df["Comparison Sector"] == comp_sector)
            & (pd.notna(df["Comparison Subsector"]))
        ]
        for index, row in sector_df.iterrows():
            subsector = row[1]
            if row[2] != row[2]:
                ct_sectors = [""]
            else:
                ct_sectors = get_sector_list(row[2])
            if tab_name == "pik-tp-aggregate-up":
                inv_sectors = [str(row[3])]
            else:
                if row[3] != row[3]:
                    inv_sectors = [""]
                else:
                    inv_sectors = get_sector_list(row[3])
            if subsector not in subsector_map[comp_sector]:
                subsector_map[comp_sector][subsector] = {}
            subsector_map[comp_sector][subsector]["climate-trace"] = ct_sectors
            if tab_name == "unfccc-aggregate-up":
                subsector_map[comp_sector][subsector]["unfccc_annex_1"] = inv_sectors
            else:
                subsector_map[comp_sector][subsector][
                    inventory_titles[tab_name]
                ] = inv_sectors

    return subsector_map


if __name__ == "__main__":
    # get sector comparison dictionary for inventories that can all be aggregated to similar sectors
    generate_sector_comparison_dict()

    # create subsector dictionary, by inventory, for more granular subsector comparions
    subsector_dictionary = {}

    for tab in tabs:
        subsector_map_json = generate_subsector_comparison_dict(tab)
        subsector_dictionary[inventory_titles[tab]] = subsector_map_json
        if tab in [
            "pik-tp-aggregate-up",
            "carbon-monitor-aggregate-up",
            "gcp-aggregate-up",
        ]:
            # some inventories cannot be aggregated to the same main sectors above, so these inventories get their own dictionary
            generate_inventory_specific_sector_comparison_dicts(tab)

    with open("files/subsector_dictionary.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(subsector_dictionary, indent=2, sort_keys=True))
