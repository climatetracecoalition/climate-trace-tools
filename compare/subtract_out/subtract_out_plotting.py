import os
import pandas as pd
import json
import numpy as np
from compare.subtract_out.util.constants import convert_numeric
from compare.subtract_out.util.data_handler import load_data
from compare.subtract_out.util.prep_data_to_plot import create_plots

path = os.getcwd()


class SectorComparison:
    def __init__(self):
        # self.data_handler = csv_handler
        # self.allinv = self.data_handler.load_data()
        self.allinv = load_data()

        with open("files/master_comparison_dict_annex1.json", "r") as f:
            self.master_comparison_dict_annex1 = json.loads(f.read())

        with open("files/master_comparison_dict_nonannex1.json", "r") as f:
            self.master_comparison_dict_nonannex1 = json.loads(f.read())

        with open("files/title_dict_nonannex1.json", "r") as f:
            self.title_dict_nonannex1 = json.loads(f.read())

        with open("files/title_dict_annex1.json", "r") as f:
            self.title_dict_annex1 = json.loads(f.read())

    def plot(
        self,
        countries,
        sectors,
        gases,
        co2eqs,
        plot_type,
        start_year,
        end_year,
        create_folders=False,
        plot_live=True,
    ):
        ############################
        # Get the data
        ############################
        # Init the Data Handler
        # dh = DataHandler()
        # allinv = load_data()
        ############################
        # Transform the data into dataframe for graphs
        # allinv = dh.load_data(years_to_columns=True)
        COMP_YEARS = list(range(start_year, end_year))
        COL_ORDER = ["Data source", "ID", "Sector", "Gas", "Unit"] + COMP_YEARS
        self.allinv = self.allinv[COL_ORDER]

        self.allinv.columns = [convert_numeric(c) for c in self.allinv.columns]
        # can only make ratios for
        ratiocols = [
            "Data source",
            "ID",
            "Sector",
            "Gas",
            "Unit",
            "carbon_eq",
            2015,
            2016,
            2017,
            2018,
            2019,
            2020,
            2021,
            2022,
        ]
        ratio_data = pd.DataFrame(columns=ratiocols)

        comparison_dicts = {}
        comparison_dicts["annex1"] = self.master_comparison_dict_annex1
        comparison_dicts["nonannex1"] = self.master_comparison_dict_nonannex1

        title_dicts = {}
        title_dicts["annex1"] = self.title_dict_annex1
        title_dicts["nonannex1"] = self.title_dict_nonannex1

        for gas in gases:
            for co2eq in co2eqs:
                for plot_type in plot_type:
                    if co2eq == "none" and gas == "all":
                        print('WARNING: Must select a co2eq if gases is "all"')
                        continue
                    if co2eq == "none" and plot_type == "gases":
                        print('WARNING: Must select a co2eq if plot type is "gases"')
                        continue
                    if gas != "all" and plot_type == "gases":
                        print('WARNING: If plot type is "gases", gas must be "all"')
                        continue
                    if gas == "co2" and co2eq != "none":
                        print('WARNING: If "gas" is "co2", "co2eq" must be "none"')
                        continue

                    if create_folders:
                        try:
                            os.makedirs(
                                path
                                + "/processed_data/"
                                + gas
                                + "/"
                                + co2eq
                                + "/"
                                + plot_type
                            )
                            print("Output folder created.")
                        except OSError:
                            print("Output folder already exists.")

                    for sector in sectors:
                        if gas != "all":
                            years_cols = self.allinv.filter(regex="\d").columns
                            gas_present = self.allinv.loc[
                                (self.allinv["Data source"] == "climate-trace")
                                & (self.allinv["Sector"] == sector)
                                & (self.allinv["Gas"] == gas),
                                years_cols,
                            ].sum()
                            if all(gas_present == 0):
                                print(
                                    f"WARNING: {gas} is not present in {sector} Climate TRACE data, cannot do comparison."
                                )
                                continue
                        if create_folders:
                            try:
                                os.makedirs(
                                    path
                                    + "/processed_data/"
                                    + gas
                                    + "/"
                                    + co2eq
                                    + "/"
                                    + plot_type
                                    + "/"
                                    + sector
                                )
                                print("Output folder created.")
                            except OSError:
                                print("Output folder already exists.")

                            try:
                                os.makedirs(
                                    path + "/processed_data/ratio_dfs/" + sector
                                )
                                print("Output folder created.")
                            except OSError:
                                print("Output folder already exists.")

                        # create plots for all listed countries, sector by sector
                        raw_data = create_plots(
                            self.allinv,
                            countries,
                            sector,
                            gas,
                            co2eq,
                            plot_type,
                            ratio_data,
                            output_folder=path
                            + "/processed_data/"
                            + gas
                            + "/"
                            + co2eq
                            + "/"
                            + plot_type
                            + "/"
                            + sector,
                            comparison_dicts=comparison_dicts,
                            title_dicts=title_dicts,
                            create_folders=create_folders,
                            plot_live=plot_live,
                        )

                        ratio_data_column_order = [
                            "Data source",
                            "ID",
                            "Sector",
                            "Gas",
                            "Unit",
                            "carbon_eq",
                            2000,
                            2001,
                            2002,
                            2003,
                            2004,
                            2005,
                            2006,
                            2007,
                            2008,
                            2009,
                            2010,
                            2011,
                            2012,
                            2013,
                            2014,
                            2015,
                            2016,
                            2017,
                            2018,
                            2019,
                            2020,
                            2021,
                            2022,
                        ]

                        raw_data = raw_data[ratio_data_column_order]
                        ratio_data = raw_data.copy()
                        # create ratios dataset
                        years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
                        totcols = [
                            "Data source",
                            "ID",
                            "Gas",
                            2015,
                            2016,
                            2017,
                            2018,
                            2019,
                            2020,
                            2021,
                            2022,
                        ]
                        grpcols = ["Data source", "ID", "Gas"]
                        country_totals = (
                            ratio_data[totcols]
                            .groupby(grpcols, as_index=False)
                            .sum(min_count=1)
                        )
                        country_totals.to_csv(
                            path
                            + f"/processed_data/ratio_dfs/{sector}/{sector}_raw_data.csv",
                            index=False,
                        )
                        for yr in years:
                            ratio_data[f"inv_to_ct_ratio_{yr}"] = ""
                        for index, row in ratio_data.iterrows():
                            for yr in years:
                                val_list = ratio_data.loc[
                                    (ratio_data["Sector"] == row["Sector"])
                                    & (ratio_data["ID"] == row["ID"])
                                    & (ratio_data["Gas"] == row["Gas"])
                                    & (ratio_data["Data source"] == "climate-trace"),
                                    yr,
                                ].tolist()
                                if len(val_list) > 0:
                                    value = val_list[0]
                                    if (
                                        (isinstance(row[yr], float))
                                        or (isinstance(row[yr], int))
                                    ) and (
                                        (isinstance(value, float))
                                        or (isinstance(value, int))
                                    ):
                                        if not np.isnan(row[yr]) and not np.isnan(
                                            value
                                        ):
                                            if value != 0:
                                                sect_ratio = row[yr] / value
                                                ratio_data.loc[
                                                    (
                                                        ratio_data["Sector"]
                                                        == row["Sector"]
                                                    )
                                                    & (ratio_data["ID"] == row["ID"])
                                                    & (ratio_data["Gas"] == row["Gas"])
                                                    & (
                                                        ratio_data["Data source"]
                                                        == row["Data source"]
                                                    ),
                                                    f"sect_ratio_{yr}",
                                                ] = sect_ratio

                        ratio_data = ratio_data.rename(
                            columns={
                                "Data source": "reporting_entity",
                                "ID": "iso3_country",
                                "Sector": "climate_trace_sector",
                                "Unit": "unit",
                            }
                        )

                        ratio_data.to_csv(
                            path
                            + f"/processed_data/ratio_dfs/{sector}/{sector}_ratio_data.csv",
                            index=False,
                        )
