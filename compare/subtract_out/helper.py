import json
from compare.compare.subtract_out.util.country_lists import (countries_annex1, countries_nonannex1)


class InputHelper:
    def __init__(self):
        with open('files/master_comparison_dict_annex1.json', 'r') as f:
            self.master_comparison_dict_annex1 = json.loads(f.read())

        with open('files/master_comparison_dict_nonannex1.json', 'r') as f:
            self.master_comparison_dict_nonannex1 = json.loads(f.read())

    def get_available_countries(self, annex1):
        if annex1:
            return countries_annex1
        else:
            return countries_nonannex1

    def sectors_available_to_plot(self, annex1):
        if annex1:
            compdict = self.master_comparison_dict_annex1
        else:
            compdict = self.master_comparison_dict_nonannex1

        return list(compdict.keys())


    def inventories_available_to_compare_for_sector(self, sector, annex1):
        if annex1:
            compdict = self.master_comparison_dict_annex1
        else:
            compdict = self.master_comparison_dict_nonannex1

        return list(compdict[sector].keys())

