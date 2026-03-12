from setuptools import setup, find_packages

setup(
    name="climate_trace_tools",
    version="1.0.0",
    description="Tools for working with Climate TRACE emissions data, including inventory comparison, asset finding, and ownership analysis",
    author="Christy Lewis",
    author_email="christy@watttime.org",
    license="CC-BY-4.0",
    install_requires=[
        "numpy",
        "pandas",
        "plotly",
        "openpyxl",
        "shapely",
        "geopy",
        "google-cloud-bigquery",
        "db-dtypes",
        "requests",
        "networkx",
        "tqdm",
    ],
    packages=find_packages(),  # This ensures that all packages and sub-packages are included
    include_package_data=True,  # This tells setuptools to include files specified in MANIFEST.in or package_data
    package_data={
        "climate_trace_tools": [
            "data/country/*.zip",
            "data/source/*.zip",
            "data/ownership/*.zip",
            "data/supplementary/*.csv",
            "compare/subtract_out/files/*.csv",
            "compare/subtract_out/files/*.xlsx",
            "compare/subtract_out/files/*.json",
            "compare/aggregate_up/files/*.xlsx",
            "compare/aggregate_up/files/*.json",
        ]
    },
)
