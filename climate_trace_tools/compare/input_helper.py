import json
from climate_trace_tools.compare.subtract_out.util.country_lists import (
    countries_annex1,
    countries_nonannex1,
)
import importlib.resources as pkg_resources
from climate_trace_tools.compare.subtract_out import files as so_files
from climate_trace_tools.compare.aggregate_up import files as au_files


class InputHelper:
    def __init__(self):
        with pkg_resources.open_text(
            so_files, "master_comparison_dict_annex1.json"
        ) as f:
            self.master_comparison_dict_annex1 = json.loads(f.read())

        with pkg_resources.open_text(
            so_files, "master_comparison_dict_nonannex1.json"
        ) as f:
            self.master_comparison_dict_nonannex1 = json.loads(f.read())

    def get_available_countries(self, annex1: bool):
        """

        :param annex1: bool, true indicates annex1 country, false indicates non annex 1 country
        :return: list of countries
        """
        if annex1:
            return countries_annex1
        elif not annex1:
            return countries_nonannex1
        elif annex1 == "all":
            return countries_nonannex1 + countries_annex1

    def sectors_available_to_plot_subtract_out(self, annex1: bool):
        """

        :param annex1: bool, true indicates annex1 country, false indicates non annex 1 country
        :return: list of climate trace sectors for which comparisons are avilable
        """
        if annex1:
            compdict = self.master_comparison_dict_annex1
        else:
            compdict = self.master_comparison_dict_nonannex1

        return list(compdict.keys())

    def inventories_available_to_compare_for_sector_subtract_out(
        self, sector: str, annex1: bool
    ):
        """

        :param sector: climate-trace sector that you are generating comparison for
        :param annex1: True if the country you are evaluating is annex1, false for nonannex1
        :return: list of inventories that are available to compare to that sector
        """
        if annex1:
            compdict = self.master_comparison_dict_annex1
        else:
            compdict = self.master_comparison_dict_nonannex1

        return list(compdict[sector].keys())

    def get_sector_options_aggregate_up(self, inventory: str):
        """
        :param inventory: str, name of inventory for comparison
        :return: list of sectors available for comparison
        """
        with pkg_resources.open_text(au_files, "subsector_dictionary.json") as f:
            sector_dictionary = json.loads(f.read())

        inventory_dict = sector_dictionary[inventory]
        inventory_sectors = list(inventory_dict.keys())

        return inventory_sectors

    def get_subsector_options_aggregate_up(self, inventory: str):
        """
        :param inventory: name of inventory for comparison
        :return: list of subsectors available for comparison
        """
        with pkg_resources.open_text(au_files, "subsector_dictionary.json") as f:
            sector_dictionary = json.loads(f.read())

        inventory_dict = sector_dictionary[inventory]
        subsectors = []

        for sectors, sdict in inventory_dict.items():
            subsectors.append(list(sdict.keys()))

        return subsectors
