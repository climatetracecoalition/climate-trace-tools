import pandas as pd

from climate_trace_tools.compare.subtract_out import files
import importlib.resources as pkg_resources


def load_title_conversion():
    with pkg_resources.open_text(
        files,
        "CT_country_titles.csv",
    ) as csv_path:
        return pd.read_csv(csv_path).applymap(lambda x: x.strip(" "))


TITLE_CONVERSION = load_title_conversion()


def load_gas_titles():
    with pkg_resources.open_text(files, "gas_title_dict.csv") as csv_path:
        return pd.read_csv(csv_path).applymap(lambda x: x.strip(" "))


GAS_TITLES = load_gas_titles()
# CODE_CONVERSION = pd.read_csv('../../../../data/supplementary/countries.csv').applymap(lambda x: x.strip(' '))


# Dictionaries convert database column names to db_connect column names
DB_SOURCE_TO_COL_NAME = {
    "original_inventory_sector": "Sector",
    "iso3_country": "ID",
    "reporting_entity": "Data source",
    "gas": "Gas",
    "emissions_quantity_units": "Unit",
}

COL_NAME_TO_DB_SOURCE = {
    "Sector": "original_inventory_sector",
    "ID": "iso3_country",
    "Data source": "reporting_entity",
    "Gas": "gas",
    "Unit": "emissions_quantity_units",
}


def get_code_conversion():
    df = pd.read_csv("../../../data/supplementary/countries.csv")
    df = df.rename(columns={"name": "country_name"})
    df = df[["iso3", "iso3", "country_name"]]
    CODE_CONVERSION = df.applymap(lambda x: x.strip(" "))

    return CODE_CONVERSION


def get_country_name(iso3):
    CODE_CONVERSION = get_code_conversion()
    if iso3 not in CODE_CONVERSION["iso3"].values:
        return None

    return CODE_CONVERSION.loc[CODE_CONVERSION["iso3"] == iso3, "country_name"].values[
        0
    ]


def get_country_title(iso3):
    if iso3 not in TITLE_CONVERSION["iso3"].values:
        return None

    return TITLE_CONVERSION.loc[
        TITLE_CONVERSION["iso3"] == iso3, "country_title"
    ].values[0]


def get_gas_title(gas):
    if gas not in GAS_TITLES["formula"].values:
        return "CO<sub>2</sub>e"

    return GAS_TITLES.loc[GAS_TITLES["formula"] == gas, "title"].values[0]


def convert_numeric(x):
    if str(x).endswith("ff"):
        return x
    try:
        return int(x)
    except Exception:
        try:
            return float(x)
        except Exception:
            return x
