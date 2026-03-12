![climateTRACE-logo](https://github.com/climatetracecoalition/climate-trace-tools/assets/43048648/abd1edac-488e-4dfd-b545-6cf3b79f3291)

# climate-trace-tools 

This repository contains tools and data to make comparing emissions data easier for the climate data community.

## Resources

### Schema

The schema folder contains Climate TRACE's common data format. Climate TRACE believes this format to be the most generic and inclusive format for storing data from many inventories and sources.

### Data

The data folder contains all of the data that Climate TRACE has scraped and process to date. This includes country data, and source (asset) level data. The data will be updated as it becomes available. All of the data in this folder is stored in the format described in Schema. More information can be found [here](climate_trace_tools/schema/README.md).

## Tools

### Compare

This folder contains many tools to help compare data across different sources and inventories. More information on the tools availble can be found [here](climate_trace_tools/compare/README.md).

### Asset Finder

The asset_finder folder contains a tool for finding Climate TRACE point assets within a given location and buffer zone radius, along with their emissions data and regional (GADM) benchmarks. It queries Climate TRACE's BigQuery tables. More information can be found [here](climate_trace_tools/asset_finder/README.md).

### Ownership

The ownership folder contains a tool for looking up asset ownership information and retrieving associated emissions data via the Climate TRACE API. More information can be found [here](climate_trace_tools/ownership/README.md).

## Installation

Run the following in your terminal.

This repository uses [Git LFS](https://git-lfs.github.com/) for large data files. If you don't have Git LFS installed, follow the instructions at https://git-lfs.github.com/ before proceeding.

```bash
git lfs install
pip install git+https://github.com/climatetracecoalition/climate-trace-tools.git
```

## License

This repository is licensed under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE) license, consistent with Climate TRACE's open data license.

## Credits

Christy Lewis \
Mikey Abela \
Lee Gans \
Krsna Raniga \
Lekha Sridhar \
Peter Thomas \
Gabriela de Volpato \
Amy Piscopo \
Ishan Saraswat \
Anna Mowat \
Amy Kouch

