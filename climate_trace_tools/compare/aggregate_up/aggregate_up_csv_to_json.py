import pandas as pd
import json
import re

# Specify the path to the XLSX file with the comparison dictionaries.
# and then put it in the spreadsheets directory within this directory

xlsx_file_path = "files/aggregate-up-csv-crosswalks.xlsx"

# Define the list of tabs in your XLSX (assuming each tab corresponds to a separate sheet)
tabs = [
    "unfccc-aggregate-up",
    "unfccc-crt-aggregate-up",
    "edgar-aggregate-up",
    "cait-aggregate-up",
    "pik-tp-aggregate-up",
    "faostat-aggregate-up",
    "carbon-monitor-aggregate-up",
    "gcp-aggregate-up",
    "ceds-aggregate-up",
]

inventory_titles = {
    "unfccc-aggregate-up": "unfccc",
    "unfccc-crt-aggregate-up": "unfccc_crt",
    "edgar-aggregate-up": "edgar",
    "cait-aggregate-up": "cait",
    "pik-tp-aggregate-up": "pik-tp",
    "faostat-aggregate-up": "faostat",
    "carbon-monitor-aggregate-up": "carbon-monitor",
    "gcp-aggregate-up": "gcp",
    "ceds-aggregate-up": "ceds",
}


# UNFCCC tabs hold separate annex 1 / non annex 1 columns; values are the reporting_entity prefix
unfccc_tabs = {
    "unfccc-aggregate-up": "unfccc",
    "unfccc-crt-aggregate-up": "unfccc_crt",
}


def get_sector_list(raw_list, tab_name=None):
    # CRT sector names can contain ", " themselves (e.g. "1.A.2.d. Pulp, paper and print"), so only
    # split where the next item starts with a sector code
    if tab_name == "unfccc-crt-aggregate-up":
        return re.split(r",\s*(?=\d+\.)", raw_list)
    # the original UNFCCC tab has the same issue (e.g. "1.A.2.d  Pulp, Paper and Print"), but also a
    # few names without a sector code, so split before those too
    if tab_name == "unfccc-aggregate-up":
        return re.split(r",\s*(?=\d+\.|International |Marine\b|Aviation\b)", raw_list)
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
            if tab_name in unfccc_tabs:
                # UNFCCC sectors are hierarchical, so only use the sector total row (subsector left
                # blank or repeating the sector name) to avoid double counting its subsectors
                filtered_df = filtered_df[
                    filtered_df["Comparison Subsector"].isna()
                    | (filtered_df["Comparison Subsector"] == filtered_df["Comparison Sector"])
                ]

            ct_sectors = []
            inv_sectors = []
            if tab_name in unfccc_tabs:
                inv_2_sectors = []

            for index, row in filtered_df.iterrows():
                # Climate TRACE sector lists come from the other inventory tabs; the UNFCCC tabs are
                # read first, so letting their total rows set them would override every inventory's
                if pd.notna(row[2]) and tab_name not in unfccc_tabs:
                    ct_sectors = ct_sectors + get_sector_list(row[2])
                if pd.notna(row[3]):
                    inv_sectors = inv_sectors + get_sector_list(row[3], tab_name)
                if tab_name in unfccc_tabs:
                    if pd.notna(row[4]):
                        inv_2_sectors = inv_2_sectors + get_sector_list(row[4], tab_name)

            if "climate-trace" not in sector_map[comp_sector] and len(ct_sectors) > 0:
                sector_map[comp_sector]["climate-trace"] = ct_sectors
            if tab_name in unfccc_tabs:
                prefix = unfccc_tabs[tab_name]
                if len(inv_sectors) > 0:
                    sector_map[comp_sector][f"{prefix}_annex_1"] = inv_sectors
                if len(inv_2_sectors) > 0:
                    sector_map[comp_sector][f"{prefix}_non_annex_1"] = inv_2_sectors
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
        if tab_name in unfccc_tabs:
            # the UNFCCC sector total row (subsector repeating the sector name) only belongs in the
            # sector comparison dict; as a subsector it would be stacked on top of its own subsectors
            sector_df = sector_df[sector_df["Comparison Subsector"] != comp_sector]
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
                    inv_sectors = get_sector_list(row[3], tab_name)
            if subsector not in subsector_map[comp_sector]:
                subsector_map[comp_sector][subsector] = {}
            subsector_map[comp_sector][subsector]["climate-trace"] = ct_sectors
            if tab_name in unfccc_tabs:
                subsector_map[comp_sector][subsector][
                    f"{unfccc_tabs[tab_name]}_annex_1"
                ] = inv_sectors
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
