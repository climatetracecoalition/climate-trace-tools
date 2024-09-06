import os
import pandas as pd
import json
import numpy as np
from climate_trace_tools.compare.subtract_out.util.constants import convert_numeric
from climate_trace_tools.compare.data_handler import CsvDataHandler
from climate_trace_tools.compare.subtract_out.util.prep_data_to_plot import create_plots
import importlib.resources as pkg_resources
from climate_trace_tools.compare.subtract_out import files
import datetime
from climate_trace_tools.compare.subtract_out.util.logger_setup import logger

path = os.getcwd()


class SectorComparison:
    def __init__(self, data_handler=CsvDataHandler(), dh_type="csv"):
        self.allinv = data_handler.load_all_data()
        self.dh_type = dh_type
        self.release = getattr(data_handler, "release", None)

        with pkg_resources.open_text(files, "master_comparison_dict_annex1.json") as f:
            self.master_comparison_dict_annex1 = json.loads(f.read())

        with pkg_resources.open_text(
            files, "master_comparison_dict_nonannex1.json"
        ) as f:
            self.master_comparison_dict_nonannex1 = json.loads(f.read())

        with pkg_resources.open_text(files, "title_dict_nonannex1.json") as f:
            self.title_dict_nonannex1 = json.loads(f.read())

        with pkg_resources.open_text(files, "title_dict_annex1.json") as f:
            self.title_dict_annex1 = json.loads(f.read())

        # Perform forward-filling
        self._forward_fill_data()

    def _forward_fill_data(self):
        # Identify year columns
        year_columns = [col for col in self.allinv.columns if str(col).isdigit()]
        year_columns.sort()

        # Create a new DataFrame for forward-fill information
        ff_data = pd.DataFrame(
            index=self.allinv.index, columns=[f"{year}_ff" for year in year_columns]
        )

        # Calculate last true year
        self.allinv["last_true_year"] = self.allinv[year_columns].apply(
            lambda x: x.last_valid_index(), axis=1
        )

        # Forward fill the data
        filled_data = self.allinv[year_columns].ffill(axis=1)

        # Create boolean mask for forward-filled values
        for year in year_columns:
            year_int = int(year)
            ff_data[f"{year}_ff"] = self.allinv["last_true_year"].apply(
                lambda x: pd.notna(x) and int(x) < min(year_int, 2023)
            )

        # Combine original data with filled data and forward-fill information
        self.allinv = pd.concat(
            [
                self.allinv.drop(columns=year_columns),
                filled_data,
                ff_data,
            ],
            axis=1,
        )

    def plot(
        self,
        countries,
        sectors,
        gases,
        co2eqs,
        plot_type,
        start_year,
        end_year,
        name,
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
        COMP_YEARS = list(range(start_year, end_year + 1))
        FF_COLS = [f"{year}_ff" for year in COMP_YEARS]

        COL_ORDER = (
            ["Data source", "ID", "Sector", "Gas", "Unit", "last_true_year"]
            + COMP_YEARS
            + FF_COLS
        )
        self.allinv = self.allinv[COL_ORDER]

        self.allinv.columns = [convert_numeric(c) for c in self.allinv.columns]
        # can only make ratios for
        ratiocols = [
            "Data source",
            "ID",
            "Sector",
            "Gas",
            "Unit",
            "last_true_year",
            "carbon_eq",
            2015,
            2016,
            2017,
            2018,
            2019,
            2020,
            2021,
            2022,
            2023,
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

                    # determine if using database data_handler

                    if self.dh_type == "db":
                        release = self.release
                        base_folder = f"/processed_data_{release}/"
                    else:
                        base_folder = "/processed_data/"

                    if create_folders:
                        try:
                            os.makedirs(
                                path + base_folder + gas + "/" + co2eq + "/" + plot_type
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
                            + base_folder
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

                        if not raw_data.empty:
                            # Create folders only if data is returned
                            if create_folders:
                                # Create directory for ratio_dfs before saving CSV
                                ratio_dfs_path = os.path.join(
                                    path + base_folder, "ratio_dfs", sector
                                )
                                os.makedirs(ratio_dfs_path, exist_ok=True)

                            ratio_data_column_order = [
                                "Data source",
                                "ID",
                                "Sector",
                                "Gas",
                                "Unit",
                                "carbon_eq",
                                "data_available",
                                "last_true_year",
                                2015,
                                2016,
                                2017,
                                2018,
                                2019,
                                2020,
                                2021,
                                2022,
                                2023,
                            ]

                            raw_data = raw_data[ratio_data_column_order]
                            ratio_data = raw_data.copy()
                            # create ratios dataset
                            years = [
                                2015,
                                2016,
                                2017,
                                2018,
                                2019,
                                2020,
                                2021,
                                2022,
                                2023,
                            ]
                            totcols = [
                                "Data source",
                                "ID",
                                "Gas",
                                "data_available",
                                "last_true_year",
                                2015,
                                2016,
                                2017,
                                2018,
                                2019,
                                2020,
                                2021,
                                2022,
                                2023,
                            ]
                            grpcols = [
                                "Data source",
                                "ID",
                                "Gas",
                                "data_available",
                                "last_true_year",
                            ]
                            country_totals = (
                                ratio_data[totcols]
                                .groupby(grpcols, as_index=False)
                                .sum(min_count=1)
                            )

                            country_totals = country_totals.rename(
                                columns={
                                    "Data source": "reporting_entity",
                                    "ID": "iso3_country",
                                    "Sector": "climate_trace_sector",
                                }
                            )

                            timestamp = datetime.datetime.now().strftime("%Y%m%d")

                            # Save CSV files
                            csv_path = os.path.join(
                                ratio_dfs_path, f"{sector}_raw-data_{name}.csv"
                            )
                            country_totals.to_csv(csv_path, index=False)
                            logger.info(f"Saved raw data to: {csv_path}")

                            for yr in years:
                                ratio_data[f"inv_to_ct_ratio_{yr}"] = ""
                            for index, row in ratio_data.iterrows():
                                for yr in years:
                                    val_list = ratio_data.loc[
                                        (ratio_data["Sector"] == row["Sector"])
                                        & (ratio_data["ID"] == row["ID"])
                                        & (ratio_data["Gas"] == row["Gas"])
                                        & (
                                            ratio_data["Data source"] == "climate-trace"
                                        ),
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
                                                    # difference_tonnes = row[yr]
                                                    ratio_data.loc[
                                                        (
                                                            ratio_data["Sector"]
                                                            == row["Sector"]
                                                        )
                                                        & (
                                                            ratio_data["ID"]
                                                            == row["ID"]
                                                        )
                                                        & (
                                                            ratio_data["Gas"]
                                                            == row["Gas"]
                                                        )
                                                        & (
                                                            ratio_data["Data source"]
                                                            == row["Data source"]
                                                        ),
                                                        f"inv_to_ct_ratio_{yr}",
                                                    ] = sect_ratio

                            ratio_data = ratio_data.rename(
                                columns={
                                    "Data source": "reporting_entity",
                                    "ID": "iso3_country",
                                    "Sector": "climate_trace_sector",
                                    "Unit": "unit",
                                }
                            )

                            csv_path = os.path.join(
                                ratio_dfs_path, f"{sector}_ratio-data_{name}.csv"
                            )
                            ratio_data.to_csv(csv_path, index=False)
                            logger.info(f"Saved ratio data to: {csv_path}")

        return ratio_data
