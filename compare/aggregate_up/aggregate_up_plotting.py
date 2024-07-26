import pandas
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly
import geopandas as gpd
import json
from aggregate_up_util import *

fonts = {"family": "Foros, medium"}


class CountryPlotting:
    def __init__(self, iso3_country):
        """
        Pulls data for all three inventories, climate-trace, unfccc_non_annex_1, and unfccc_annex_1
        for the chosen country. Within functions the appropriate unfccc inventory is selected based
        on chosen country.
        """

        if iso3_country:
            self.country = iso3_country
        else:
            self.country = False

        self.climate_trace = read_zip("climate-trace", iso3_country)
        self.unfccc_non_annex_1 = read_zip("unfccc_non_annex_1", iso3_country)
        self.unfccc_annex_1 = read_zip("unfccc_annex_1", iso3_country)
        self.edgar = read_zip("edgar", iso3_country)
        self.pik_tp = read_zip("pik-tp", iso3_country)
        self.cait = read_zip("cait", iso3_country)
        self.carbon_monitor = read_zip("carbon-monitor", iso3_country)
        self.non_annex_iso3 = self.unfccc_non_annex_1["iso3_country"].unique()
        self.annex_iso3 = self.unfccc_annex_1["iso3_country"].unique()

        self.gas_gwps = get_ghg_gwps_list()
        self.tick_label_dict = get_tick_label_dict()

        with open("files/comparison_sector_dictionary.json", "r") as f:
            self.comparison_sector_dictionary = json.loads(f.read())

        with open("files/comparison_sector_dictionary_fires.json", "r") as f:
            self.comparison_sector_dictionary_fires = json.loads(f.read())

        with open("files/comparison_sector_dictionary_carbon-monitor.json", "r") as f:
            self.comparison_sector_dictionary_carbon_monitor = json.loads(f.read())

        with open("files/comparison_sector_dictionary_gcp.json", "r") as f:
            self.comparison_sector_dictionary_gcp = json.loads(f.read())

        with open("files/comparison_sector_dictionary_pik-tp.json", "r") as f:
            self.comparison_sector_dictionary_pik = json.loads(f.read())

        with open("files/subsector_dictionary.json", "r") as f:
            self.subsector_dictionary = json.loads(f.read())

    def get_latest_year_for_inventory(
        self,
        ClimateTRACE=False,
        UNFCCC=False,
        EDGAR=False,
        CAIT=False,
        PIK=False,
        GCP=False,
        CarbonMonitor=False,
    ):
        if ClimateTRACE:
            return self.climate_trace["start_time"].max()
        elif UNFCCC:
            if self.country in self.annex_iso3:
                return self.unfccc_annex_1["start_time"].max()
            else:
                return self.unfccc_non_annex_1["start_time"].max()
        elif EDGAR:
            return self.edgar["start_time"].max()
        elif CAIT:
            return self.cait["start_time"].max()
        elif PIK:
            return self.pik_tp["start_time"].max()
        elif CarbonMonitor:
            return self.carbon_monitor["start_time"].max()

    def get_all_sector_comparison_data(
        self,
        ClimateTRACE,
        UNFCCC,
        EDGAR,
        CAIT,
        PIK,
        GCP,
        CarbonMonitor,
        lulucf,
        plotting_dict,
    ):
        """
        Returns dictionary that includes requested inventories with parent sector mappings + requested data years

        'ClimateTRACE', 'UNFCCC', 'EDGAR', 'CAIT', 'PIK','GCP', 'CarbonMonitor should be booleans indicating whether to
        include that inventory's data. Note: PIK, GCP, and CarbonMonitor can only be compared to Climate TRACE, so only
        one of these inputs can be True in addition to Climate TRACE. ClimateTRACE, UNFCCC, EDGAR, and CAIT can all we
        plotted on the same graph, thus all 4 can be marked as TRUE.

        Note as of April 2024, GCP data has not been converted or uploaded so cannot be used.

        'lulucf' is an optional argument, defaults to False, set to 'True' if land use data desired.

        """
        comp_dict = {}

        if UNFCCC:
            # determine if country input is annex 1 or non annex 1
            if self.annex_iso3.size > 0:
                unfccc_name = "unfccc_annex_1"
                unfccc_df = calculate_gwp(self.unfccc_annex_1)
            else:
                unfccc_name = "unfccc_non_annex_1"
                unfccc_df = calculate_gwp(self.unfccc_non_annex_1)
            # map the parent sector onto the data imported from csvs for later aggregation
            all_sector_unfccc = parent_sector_map(
                self.country, unfccc_name, unfccc_df, plotting_dict
            )
            if not lulucf:
                all_sector_unfccc = all_sector_unfccc.loc[
                    all_sector_unfccc["parent_sector"] != "Forestry and Land Use Change"
                ]
            comp_dict[unfccc_name] = all_sector_unfccc

        if EDGAR:
            edgar_mask = self.edgar["gas"].isin(
                list(self.gas_gwps["lower_designation"])
            )
            edgar_masked = self.edgar[edgar_mask]
            edgar_df = calculate_gwp(edgar_masked)
            all_sector_edgar = parent_sector_map(
                self.country, "edgar", edgar_df, plotting_dict
            )
            # no need to remove lulucf as edgar does not include land use data
            comp_dict["edgar"] = all_sector_edgar

        if ClimateTRACE:
            all_sector_ct = parent_sector_map(
                self.country, "climate-trace", self.climate_trace, plotting_dict
            )
            if not lulucf:
                all_sector_ct = all_sector_ct.loc[
                    all_sector_ct["parent_sector"] != "Forestry and Land Use Change"
                ]
            # EDGAR doesn't include international aviation, so remove it if its included in the comparison
            if EDGAR:
                all_sector_ct = all_sector_ct.loc[
                    all_sector_ct["original_inventory_sector"]
                    != "international-aviation"
                ]
            comp_dict["climate-trace"] = all_sector_ct

        if CAIT:
            cait_df = calculate_gwp(self.cait)
            all_sector_cait = parent_sector_map(
                self.country, "cait", cait_df, plotting_dict
            )
            if not lulucf:
                all_sector_cait = all_sector_cait[
                    all_sector_cait.original_inventory_sector
                    != "Land-Use Change and Forestry "
                ]
            comp_dict["cait"] = all_sector_cait

        if PIK:
            pik_df = calculate_gwp(self.pik_tp)
            all_sector_pik = parent_sector_map(
                self.country, "pik-tp", pik_df, plotting_dict
            )
            if not lulucf:
                all_sector_pik = all_sector_pik[
                    all_sector_pik.original_inventory_sector != "M.LULUCF"
                ]
            comp_dict["pik-tp"] = all_sector_pik

        if CarbonMonitor:
            cm_df = calculate_gwp(self.carbon_monitor)
            all_sector_cm = parent_sector_map(
                self.country, "carbon-monitor", cm_df, plotting_dict
            )
            comp_dict["carbon-monitor"] = all_sector_cm

        return comp_dict

    def single_year_comparison_totals(
        self,
        year,
        unfccc_year,
        UNFCCC=False,
        EDGAR=False,
        PIK=False,
        CAIT=False,
        color_dict=inventory_color_map(),
        lulucf=False,
    ):
        """
        Returns barchart for selected inventories ANNUAL TOTALS vs Climate TRACE data for a single chosen year.

        'year' should be a numeric value.

        'unfccc_year' should be a numeric value indicating which unfccc reporting year to compare to. Many non-annex 1
        countries will not have inventories more recent than 2015.

        'ClimateTRACE', 'UNFCCC', 'EDGAR', 'CAIT', 'PIK' should be booleans indicating whether to
        include that inventory's data. Note: PIK can only be compared to Climate TRACE, so only
        one of these inputs can be True in addition to Climate TRACE. ClimateTRACE, UNFCCC, EDGAR, and CAIT can all we
        plotted on the same graph, thus all 4 can be marked as TRUE.

        'GCP' and 'CarbonMonitor' are not options because these inventories do not measure all emissions so totals
        should not be compared.

        'lulucf' is an optional argument, defaults to False, set to 'True' if land use data desired.

        'color_dict' and 'plotting_dict' currently default to functions in plotting_dictionary,
        but in future one can use a custom dictionary if desired by adding to plotting_dictionary file.
        """
        if not (UNFCCC | EDGAR | CAIT | PIK):
            raise ValueError("An inventory must be selected for comparison")

        # select correct plotting dict based on inventories chosen for comparison
        if PIK:
            plotting_dict = self.comparison_sector_dictionary_pik
        else:
            plotting_dict = self.comparison_sector_dictionary

        GCP = False
        CarbonMonitor = False
        comp_dict = self.get_all_sector_comparison_data(
            True, UNFCCC, EDGAR, CAIT, PIK, GCP, CarbonMonitor, lulucf, plotting_dict
        )

        fig = go.Figure().update_layout(font=fonts)

        output_data = {}

        for inventory in comp_dict:
            data = comp_dict[inventory]  # isolate data for specific inventory in loop
            if (inventory == "unfccc_non_annex_1") & (unfccc_year is not False):
                mask = (
                    (data["year"] == unfccc_year)
                    & (data["gas"] == "co2e_100yr")
                    & (~data["parent_sector"].isna())
                )
                x_label = "{} {}".format(unfccc_year, self.tick_label_dict[inventory])
            else:
                mask = (
                    (data["year"] == year)
                    & (data["gas"] == "co2e_100yr")
                    & (~data["parent_sector"].isna())
                )
                x_label = "{} {}".format(year, self.tick_label_dict[inventory])

            masked_data = (
                data[mask].groupby("year")["emissions_quantity"].sum().reset_index()
            )
            output_data[inventory] = masked_data

            fig.add_trace(
                go.Bar(
                    name=inventory,
                    x=[x_label],
                    y=masked_data["emissions_quantity"],
                    marker_color=color_dict[inventory],
                    showlegend=False,
                    text=masked_data["emissions_quantity"],
                    texttemplate="%{value:.4s}",
                )
            )

        if self.country:
            title = f"{self.country} Inventory Comparison"
        else:
            title = "Global Inventory comparison"

        fig.update_layout(
            title_text=title, font=dict(size=18), legend=dict(font=dict(size=17))
        )
        fig.update_yaxes(
            title_text="CO2eq (tonnes)",
            title_font=dict(size=17),
            tickfont=dict(size=16),
        )
        fig.update_xaxes(tickfont=dict(size=16))

        fig.show()

        return fig, output_data

    def single_year_comparison_sectors(
        self,
        gas,
        year,
        unfccc_year=False,
        UNFCCC=False,
        EDGAR=False,
        CAIT=False,
        PIK=False,
        GCP=False,
        CarbonMonitor=False,
        color_dict=sector_color_map(),
        lulucf=False,
    ):
        """
        Returns barchart for selected inventory vs Climate TRACE data for a single chosen year with breakdown
        by sectors.

        'year' should be a numberic value.

        'ClimateTRACE', 'UNFCCC', 'EDGAR', 'CAIT', 'PIK', 'GCP, and 'CarbonMonitor' should be booleans indicating whether to
        include that inventory's data. Note: PIK, GCP, and Carbon Monitor can only be compared to Climate TRACE, so only
        one of these inputs can be True in addition to Climate TRACE. ClimateTRACE, UNFCCC, EDGAR, and CAIT can all we
        plotted on the same graph, thus all 4 can be marked as TRUE.


        'lulucf' is an optional argument, defaults to False, set to 'True' if land use data desired.

        'color_dict' and 'plotting_dict' currently default to functions in plotting_dictionary,
        but in future one can use a custom dictionary if desired by adding to plotting_dictionary file.
        """
        if not (UNFCCC | EDGAR | CAIT | PIK | GCP | CarbonMonitor):
            raise ValueError("An inventory must be selected for comparison")

        # select correct plotting dict based on inventories chosen for comparison
        if PIK:
            plotting_dict = self.comparison_sector_dictionary_pik
        elif GCP:
            plotting_dict = self.comparison_sector_dictionary_gcp
        elif CarbonMonitor:
            plotting_dict = self.comparison_sector_dictionary_carbon_monitor
        else:
            plotting_dict = self.comparison_sector_dictionary

        comp_dict = self.get_all_sector_comparison_data(
            True, UNFCCC, EDGAR, CAIT, PIK, GCP, CarbonMonitor, lulucf, plotting_dict
        )

        fig = go.Figure().update_layout(font=fonts)

        parent_sectors = comp_dict["climate-trace"]["parent_sector"].unique().tolist()

        totals = {}
        for inventory, invdict in comp_dict.items():
            totals[inventory] = 0

        x_labels = []
        df = pd.DataFrame()
        for sector in parent_sectors:
            if sector != sector:
                continue
            for inventory in comp_dict:
                data = comp_dict[inventory]
                if (inventory == "unfccc_non_annex_1") & (unfccc_year is not False):
                    mask = (
                        (data["parent_sector"] == sector)
                        & (data["year"] == unfccc_year)
                        & (data["gas"] == f"{gas}")
                    )
                    x_label = "{} {}".format(
                        unfccc_year, self.tick_label_dict[inventory]
                    )
                else:
                    mask = (
                        (data["parent_sector"] == sector)
                        & (data["year"] == year)
                        & (data["gas"] == f"{gas}")
                    )
                    x_label = "{} {}".format(year, self.tick_label_dict[inventory])

                masked_data = data[mask]
                grouped_data = (
                    masked_data.groupby("year")["emissions_quantity"]
                    .sum()
                    .reset_index()
                )

                df = pd.concat([df, masked_data])

                if grouped_data.empty:
                    continue

                totals[inventory] += grouped_data.emissions_quantity.values
                x_labels.append(x_label)
                fig.add_trace(
                    go.Bar(
                        name=sector,
                        x=[x_label],
                        y=grouped_data["emissions_quantity"],
                        marker_color=color_dict[sector],
                        showlegend=(inventory == "climate-trace"),
                        text=grouped_data["emissions_quantity"],
                        textposition="inside",
                        textfont=dict(size=12),
                        texttemplate="%{value:.4s}",
                    )
                )

        totals_list = [round(float(item), 0) for key, item in totals.items()]
        x_labels = x_labels[: len(comp_dict)]

        # add totals to bars with scatter trace
        fig.add_trace(
            go.Scatter(
                x=x_labels,
                y=totals_list,
                text=totals_list,
                mode="text",
                textposition="top center",
                textfont=dict(
                    size=12,
                ),
                showlegend=False,
                texttemplate="%{text:.3s}",
            )
        )

        if self.country:
            title = f"{self.country} Inventory Comparison"
        else:
            title = "Global Inventory Comparison"

        fig.update_layout(
            title_text=title,
            barmode="stack",
            font=dict(size=18),
            legend=dict(font=dict(size=17)),
        )
        fig.update_yaxes(
            title_text=f"{gas} (tonnes)",
            title_font=dict(size=17),
            tickfont=dict(size=16),
        )
        fig.update_xaxes(tickfont=dict(size=16))

        fig.show()

        return fig, df

    def single_year_comparison_subsectors(
        self,
        gas,
        year,
        sector,
        unfccc_year=False,
        UNFCCC=False,
        EDGAR=False,
        CAIT=False,
        PIK=False,
        GCP=False,
        CarbonMonitor=False,
        color_dict=subsector_color_map(),
    ):
        """
        Returns barchart for UNFCCC (annex 1 only) or EDGAR vs Climate TRACE data for a single chosen year and sector with breakdown by subsectors.

        'year' should be a numberic value.

        'ClimateTRACE', 'UNFCCC', 'EDGAR', 'CAIT', 'PIK', 'GCP, and 'CarbonMonitor' should be booleans indicating whether to include that inventory's data. Note, only one inventory  may be selected for comparison to Climate TRACE.

        'sector' must be a key in the dictionary for the inventory you are comparing (ie. one of
        ['Energy Industries and Fugitive Emissions',
            'Manufacturing and Industrial Processes',
            'Transport',
            'Buildings',
            'Agriculture',
            'Forestry and Land Use Change',
            'Waste'] for UNFCCC, EDGAR, or Climate TRACE).

        All options for 'sector' can be found in the dictionaries stored in /files.

        If 'sector' is False, all subsectors for that inventory will be plotted.

        'lulucf' is an optional argument, defaults to False, set to 'True' if land use data desired.

        'color_dict' and 'plotting_dict' currently default to functions in plotting_dictionary,
        but in future one can use a custom dictionary if desired by adding to aggregate_up_util.
        """

        if not (UNFCCC | EDGAR | CAIT | PIK | GCP | CarbonMonitor):
            raise ValueError("Either UNFCCC or EDGAR must be used for comparison")
        if sum([EDGAR, UNFCCC, CAIT, PIK, GCP, CarbonMonitor]) > 1:
            raise ValueError("Must specify only one of UNFCCC or EDGAR")

        # select correct plotting dict based on inventories chosen for comparison
        if PIK:
            plotting_dict = self.comparison_sector_dictionary_pik
        elif GCP:
            plotting_dict = self.comparison_sector_dictionary_gcp
        elif CarbonMonitor:
            plotting_dict = self.comparison_sector_dictionary_carbon_monitor
        else:
            plotting_dict = self.comparison_sector_dictionary

        subsector_plotting_dict = self.subsector_dictionary

        comp_dict = self.get_all_sector_comparison_data(
            True,
            UNFCCC,
            EDGAR,
            CAIT,
            PIK,
            GCP,
            CarbonMonitor,
            plotting_dict=plotting_dict,
            lulucf=(sector == "Forestry and Land Use Change"),
        )
        fig = go.Figure().update_layout(font=fonts)

        if UNFCCC:
            subsector_dict = subsector_plotting_dict["unfccc_annex_1"]
        elif EDGAR:
            subsector_dict = subsector_plotting_dict["edgar"]
        elif CAIT:
            subsector_dict = subsector_plotting_dict["cait"]
        elif PIK:
            subsector_dict = subsector_plotting_dict["pik-tp"]
        elif GCP:
            subsector_dict = subsector_plotting_dict["gcp"]
        elif CarbonMonitor:
            subsector_dict = subsector_plotting_dict["carbon-monitor"]

        if (
            sector == False
        ):  # if sector is False, plot all subsectors from that inventory
            if self.country:
                title = f"{self.country}, Inventory Comparison, All Subsectors"
            else:
                title = f"Global Inventory Comparison, All subsectors"

            color_dict_flat = {}
            for key, item in color_dict.items():
                color_dict_flat.update(item)

            df = pd.DataFrame()

            for inventory in comp_dict:
                data = comp_dict[inventory]
                subsector_data = subsector_map(False, inventory, data, subsector_dict)
                if (inventory == "unfccc_non_annex_1") & (unfccc_year is not False):
                    mask = (subsector_data["year"] == unfccc_year) & (
                        subsector_data["gas"] == f"{gas}"
                    )
                    x_label = "{} {}".format(
                        unfccc_year, self.tick_label_dict[inventory]
                    )
                else:
                    mask = (subsector_data["year"] == year) & (
                        subsector_data["gas"] == f"{gas}"
                    )
                    x_label = "{} {}".format(year, self.tick_label_dict[inventory])

                masked_data = (
                    subsector_data[mask]
                    .groupby(["subsector", "year"])["emissions_quantity"]
                    .sum()
                    .reset_index()
                )

                df = pd.concat([df, masked_data])

                for subsector in masked_data.subsector:
                    fig.add_trace(
                        go.Bar(
                            name=subsector,
                            x=[x_label],
                            y=masked_data[masked_data.subsector == subsector][
                                "emissions_quantity"
                            ].values,
                            marker_color=color_dict_flat[subsector],
                            showlegend=(inventory == "climate-trace"),
                            text=masked_data["emissions_quantity"],
                            texttemplate="%{value:.4s}",
                        )
                    )

        else:  # if specific sector is chosen, plot only those subsectors
            df = pd.DataFrame()
            rows_list = []
            if self.country:
                title = f"{self.country}, {sector} Inventory Comparison"
            else:
                title = f"Global Inventory Comparison, {sector}"
            subsectors = subsector_dict.get(sector).keys()
            for subsector in subsectors:
                for inventory in comp_dict:
                    data = comp_dict[inventory]
                    subsector_data = subsector_map(
                        sector, inventory, data, subsector_dict
                    )

                    if (inventory == "unfccc_non_annex_1") & (unfccc_year is not False):
                        mask = (
                            (subsector_data["subsector"] == subsector)
                            & (subsector_data["year"] == unfccc_year)
                            & (subsector_data["gas"] == f"{gas}")
                        )
                        x_label = "{} {}".format(
                            unfccc_year, self.tick_label_dict[inventory]
                        )
                    else:
                        mask = (
                            (subsector_data["subsector"] == subsector)
                            & (subsector_data["year"] == year)
                            & (subsector_data["gas"] == f"{gas}")
                        )
                        x_label = "{} {}".format(year, self.tick_label_dict[inventory])

                    masked_data = subsector_data[mask]
                    df = pd.concat([df, masked_data])
                    masked_data_grouped = (
                        masked_data.groupby("year")["emissions_quantity"]
                        .sum()
                        .reset_index()
                    )

                    fig.add_trace(
                        go.Bar(
                            name=subsector,
                            x=[x_label],
                            y=masked_data_grouped["emissions_quantity"],
                            marker_color=color_dict.get(sector).get(subsector),
                            showlegend=(inventory == "climate-trace"),
                            text=masked_data["emissions_quantity"],
                            texttemplate="%{value:.4s}",
                        )
                    )

        fig.update_layout(
            title_text=title,
            barmode="stack",
            font=dict(size=18),
            legend=dict(font=dict(size=17)),
        )
        fig.update_yaxes(
            title_text=f"{gas} (tonnes)",
            title_font=dict(size=17),
            tickfont=dict(size=16),
        )
        fig.update_xaxes(tickfont=dict(size=16))

        fig.show()

        return fig, df

    def single_year_comparison_subsector_gases(
        self,
        year,
        sector=False,
        subsector=False,
        unfccc_year=False,
        UNFCCC=False,
        EDGAR=False,
        CAIT=False,
        PIK=False,
        GCP=False,
        CarbonMonitor=False,
        color_dict=gas_color_map(),
    ):
        """
        Returns barchart for selected invenotry vs Climate TRACE data for a single chosen year and subsector with breakdown
        by gas (c2o, n2o, and ch4 as these are currently the only gases covered by CT).

        'year' should be a numberic value.

        ClimateTRACE', 'UNFCCC', 'EDGAR', 'CAIT', 'PIK', 'GCP, and 'CarbonMonitor' should be booleans indicating whether to include that inventory's data. Note, only one inventory  may be selected for comparison to Climate TRACE.

        'sector' must be a key in the dictionary for the inventory you are comparing (ie. one of
        ['Energy Industries and Fugitive Emissions',
            'Manufacturing and Industrial Processes',
            'Transport',
            'Buildings',
            'Agriculture',
            'Forestry and Land Use Change',
            'Waste'] for UNFCCC, EDGAR, or Climate TRACE).

        All options for 'sector' can be found in the dictionaries stored in /files.

        If 'sector' is False, all subsectors for that inventory will be plotted.

        'subsector' must be a subkey of the selected 'sector' key in the dictionary used for 'subsector_plotting_dict'

        'lulucf' is an optional argument, defaults to False, set to 'True' if land use data desired.

        'color_dict' and 'plotting_dict' currently default to functions in plotting_dictionary,
        but in future one can use a custom dictionary if desired by adding to plotting_dictionary file.
        """
        if not (UNFCCC | EDGAR):
            raise ValueError("Either UNFCCC or EDGAR must be used for comparison")
        if UNFCCC and EDGAR:
            raise ValueError("Must specify only one of UNFCCC or EDGAR")

        if PIK:
            plotting_dict = self.comparison_sector_dictionary_pik
        elif GCP:
            plotting_dict = self.comparison_sector_dictionary_gcp
        elif CarbonMonitor:
            plotting_dict = self.comparison_sector_dictionary_carbon_monitor
        else:
            plotting_dict = self.comparison_sector_dictionary

        subsector_plotting_dict = self.subsector_dictionary

        if UNFCCC:
            subsector_dict = subsector_plotting_dict["unfccc_annex_1"]
        elif EDGAR:
            subsector_dict = subsector_plotting_dict["edgar"]
        elif CAIT:
            subsector_dict = subsector_plotting_dict["cait"]
        elif PIK:
            subsector_dict = subsector_plotting_dict["pik-tp"]
        elif GCP:
            subsector_dict = subsector_plotting_dict["gcp"]
        elif CarbonMonitor:
            subsector_dict = subsector_plotting_dict["carbon-monitor"]

        comp_dict = self.get_all_sector_comparison_data(
            True,
            UNFCCC,
            EDGAR,
            CAIT,
            PIK,
            GCP,
            CarbonMonitor,
            plotting_dict=plotting_dict,
            lulucf=True,
        )
        fig = go.Figure().update_layout(font=fonts)

        gases = ["co2", "ch4", "n2o"]
        df = pd.DataFrame()

        if subsector:
            filter_sector = subsector
            filter_column = "subsector"
            title = subsector
        if sector:
            filter_sector = sector
            filter_column = "parent_sector"
            title = sector

        for gas in gases:
            for inventory in comp_dict:
                data = comp_dict[inventory]
                subsector_data = subsector_map(sector, inventory, data, subsector_dict)

                if (inventory == "unfccc_non_annex_1") & (unfccc_year is not False):
                    mask = (
                        (subsector_data[f"{filter_column}"] == filter_sector)
                        & (subsector_data["year"] == unfccc_year)
                        & (subsector_data["gas"] == f"{gas}")
                    )
                    x_label = "{} {}".format(
                        unfccc_year, self.tick_label_dict[inventory]
                    )
                else:
                    mask = (
                        (subsector_data[f"{filter_column}"] == filter_sector)
                        & (subsector_data["year"] == year)
                        & (subsector_data["gas"] == f"{gas}")
                    )
                    x_label = "{} {}".format(year, self.tick_label_dict[inventory])

                masked_data = data[mask]
                df = pd.concat([df, masked_data])
                grouped_data = (
                    masked_data.groupby("year")["emissions_quantity"]
                    .sum()
                    .reset_index()
                )
                gas_info = self.gas_gwps[self.gas_gwps["lower_designation"] == gas]
                gwp_100yr = gas_info["gwp_100yr"].values[0]
                total = gwp_100yr * grouped_data["emissions_quantity"]
                fig.add_trace(
                    go.Bar(
                        name=gas,
                        x=[x_label],
                        y=total,
                        marker_color=color_dict.get(gas),
                        showlegend=(inventory == "climate-trace"),
                        text=total,
                        texttemplate="%{value:.4s}",
                    )
                )

        if self.country:
            title = f"{self.country}, {title} Inventory Comparison by Gas"
        else:
            title = f"{title} Inventory Comparison by Gas, Global"
        fig.update_layout(
            title_text=title,
            barmode="stack",
            font=dict(size=18),
            legend=dict(font=dict(size=17)),
        )
        fig.update_yaxes(
            title_text="CO2eq (tonnes)",
            title_font=dict(size=17),
            tickfont=dict(size=16),
        )
        fig.update_xaxes(tickfont=dict(size=16))

        fig.show()

        return fig, df

    # def single_year_fires_comparison(self, year):
    #     """
    #     Returns barchart for EDGAR vs Climate TRACE data for the fires sectors. This is useful to demonstrate
    #     the overestimation inherent in EDGAR's Agriculture sector as it includes all biomass burning whereas
    #     Climate TRACE includes only cropland fires, with additional fire types being categorized in Forestry
    #     and Land Use Change.
    #
    #     'year' should be a numberic value.
    #
    #     'plotting_dict' currently defaults to a function in plotting_dictionary with definitions for which
    #     original inventory sectors to include.
    #     """
    #
    #     plotting_dict = self.comparison_sector_dictionary_fires
    #     comp_dict = self.get_all_sector_comparison_data(ClimateTRACE=True, UNFCCC=False, EDGAR=True, CAIT=False, PIK=False, GCP=False, CarbonMonitor=False, plotting_dict=plotting_dict,
    #                                                     lulucf=True)
    #     fig = go.Figure().update_layout(font=fonts)
    #     tick_label_dict = {'climate-trace': 'Climate TRACE', 'edgar': 'Edgar'}
    #
    #     for inventory in comp_dict:
    #         data = comp_dict[inventory]
    #         mask = (data['parent_sector'] == 'Fires') & \
    #                (data['year'] == year) & \
    #                (data['gas'] == 'co2e_100yr')
    #         masked_data = data[mask].groupby('original_inventory_sector')['emissions_quantity'].sum().reset_index()
    #         subsectors = masked_data['original_inventory_sector'].unique()
    #         for subsector in subsectors:
    #             total = masked_data[masked_data['original_inventory_sector'] == subsector]['emissions_quantity']
    #             fig.add_trace(go.Bar(name=subsector, x=['{} {}'.format(year, tick_label_dict[inventory])],
    #                                  y=total, showlegend=True, text=total, texttemplate='%{value:.4s}'))
    #
    #     if self.country:
    #         title = f"{self.country}, Fires Inventory Comparison"
    #     else:
    #         title = "Fires Inventory Comparison, Global"
    #
    #     fig.update_layout(title_text=title, barmode='stack', font=dict(size=18),
    #                       legend=dict(font=dict(size=17)))
    #     fig.update_yaxes(title_text='CO2eq (tonnes)', title_font=dict(size=17), tickfont=dict(size=16))
    #     fig.update_xaxes(tickfont=dict(size=16))
    #
    #     fig.show()
    #
    #     return fig

    def single_inventory_all_sectors_across_years(
        self,
        years,
        ClimateTRACE=False,
        UNFCCC=False,
        EDGAR=False,
        CAIT=False,
        PIK=False,
        GCP=False,
        CarbonMonitor=False,
        color_dict=sector_color_map(),
        lulucf=False,
    ):
        """
        Returns barchart for chosen inventory data comparing emissions for ALL sectors across chosen range of years.

        'ClimateTRACE', 'UNFCCC', 'EDGAR', 'CAIT', 'PIK', 'GCP', or 'CarbonMonitor' are booleans to select which inventory you want to plot. Annex or non-annex is automatically determined in function based on chosen country, user does not need to specify.

        'years' must be an array or list.

        'lulucf' is an optional argument, defaults to False, set to 'True' if land use data desired.

        'color_dict' and 'plotting_dict' currently default to functions in plotting_dictionary,but in future one can use a custom dictionary if desired by adding to plotting_dictionary file.
        """
        if PIK:
            plotting_dict = self.comparison_sector_dictionary_pik
        elif GCP:
            plotting_dict = self.comparison_sector_dictionary_gcp
        elif CarbonMonitor:
            plotting_dict = self.comparison_sector_dictionary_carbon_monitor
        else:
            plotting_dict = self.comparison_sector_dictionary

        comp_dict = self.get_all_sector_comparison_data(
            ClimateTRACE,
            UNFCCC,
            EDGAR,
            CAIT,
            PIK,
            GCP,
            CarbonMonitor,
            lulucf,
            plotting_dict,
        )

        source = list(comp_dict.keys())[0]

        fig = go.Figure().update_layout(font=fonts)
        df = pd.DataFrame()

        for inventory in comp_dict:
            data = comp_dict[inventory]
            data = data.dropna(subset="parent_sector")
            for subsector in data["parent_sector"].unique():
                mask = (
                    (data["parent_sector"] == subsector)
                    & (data["year"].isin(years))
                    & (data["gas"] == "co2e_100yr")
                )
                subsector_data = data[mask]
                df = pd.concat([df, subsector_data])
                grouped_data = (
                    data[mask].groupby("year")["emissions_quantity"].sum().reset_index()
                )
                fig.add_trace(
                    go.Bar(
                        name=subsector,
                        x=years,
                        y=grouped_data["emissions_quantity"].values,
                        marker_color=color_dict[subsector],
                        text=grouped_data["emissions_quantity"].values,
                        texttemplate="%{value:.4s}",
                    )
                )

        fig.update_traces(marker=dict(line=dict(width=1.2, color="white")))

        if self.country:
            title = f"{source} {self.country}, GHG Emissions by Year and Sector"
        else:
            title = "GHG Emissions by Year and Sector"

        fig.update_layout(
            title_text=title,
            barmode="stack",
            font=dict(size=18),
            legend=dict(font=dict(size=17)),
        )
        fig.update_yaxes(
            title_text="CO2eq (tonnes)",
            title_font=dict(size=17),
            tickfont=dict(size=16),
        )
        fig.update_xaxes(tickfont=dict(size=16), type="category")

        fig.show()

        return fig, df

    def single_inventory_single_sector_across_years(
        self,
        years,
        sector,
        ClimateTRACE=False,
        UNFCCC=False,
        EDGAR=False,
        CAIT=False,
        PIK=False,
        GCP=False,
        CarbonMonitor=False,
        lulucf=False,
    ):
        """
        Returns barchart for chosen inventory data comparing emissions for ONE sector across chosen range of years.

        'ClimateTRACE', 'UNFCCC', 'EDGAR', 'CAIT', 'PIK', 'GCP', or 'CarbonMonitor' are booleans to select which inventory you want to plot. Annex or non-annex is automatically determined in function based on chosen country, user does not need to specify.

        'sector' is an aggregate sector as in "plotting_dictionary" and must be one of:
            ['Energy Industries and Fugitive Emissions',
            'Manufacturing and Industrial Processes',
            'Transport',
            'Buildings',
            'Agriculture',
            'Forestry and Land Use Change',
            'Waste']

        'years' must be an array or list of numerical years.

        """
        if PIK:
            plotting_dict = self.comparison_sector_dictionary_pik
        elif GCP:
            plotting_dict = self.comparison_sector_dictionary_gcp
        elif CarbonMonitor:
            plotting_dict = self.comparison_sector_dictionary_carbon_monitor
        else:
            plotting_dict = self.comparison_sector_dictionary

        comp_dict = self.get_all_sector_comparison_data(
            ClimateTRACE,
            UNFCCC,
            EDGAR,
            CAIT,
            PIK,
            GCP,
            CarbonMonitor,
            lulucf,
            plotting_dict,
        )

        source = list(comp_dict.keys())[0]

        fig = go.Figure().update_layout(font=fonts)
        color_list = [
            "#110c45",
            "#08205a",
            "#00336f",
            "#004782",
            "#005a94",
            "#006fa5",
            "#0083b4",
            "#0098c1",
            "#00adcd",
            "#2dc2d8",
            "#50d7e2",
        ]

        for inventory in comp_dict:
            all_sector = comp_dict[inventory]
            data = all_sector.loc[all_sector["parent_sector"] == sector].copy()
            color_index = 0
            subsectors = data["original_inventory_sector"].unique()
            for subsector in subsectors:
                mask = (
                    (data["year"].isin(years))
                    & (data["gas"] == "co2e_100yr")
                    & (data["original_inventory_sector"] == subsector)
                )

                subsector_data = (
                    data[mask].groupby("year")["emissions_quantity"].sum().reset_index()
                )
                fig.add_trace(
                    go.Bar(
                        name=subsector,
                        x=years,
                        y=subsector_data["emissions_quantity"].values,
                        marker_color=color_list[color_index],
                        text=subsector_data["emissions_quantity"].values,
                        texttemplate="%{value:.4s}",
                    )
                )
                color_index += 1

        fig.update_traces(marker=dict(line=dict(width=1.2, color="white")))
        if self.country:
            title = f"{source} {sector} in {self.country}"
        else:
            title = f"{source} {sector}, Global"
        fig.update_layout(
            title_text=title,
            barmode="stack",
            font=dict(size=18),
            legend=dict(font=dict(size=17)),
        )
        fig.update_yaxes(
            title_text="CO2eq (tonnes)",
            title_font=dict(size=17),
            tickfont=dict(size=16),
        )
        fig.update_xaxes(tickfont=dict(size=16), type="category")

        fig.show()

        return fig
