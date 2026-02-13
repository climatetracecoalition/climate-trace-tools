from setuptools import setup, find_packages

setup(
    name="climate_trace_tools",
    version="0.0.1",
    description="Tools for comparing climate trace data to other data sources",
    author="Christy Lewis",
    author_email="christy@watttime.org",
    install_requires=[
        "numpy",
        "pandas",
        "plotly",
        "openpyxl",
        "psycopg2",
        "shapely",
        "geopy",
        "google-cloud-bigquery",
        "requests",
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
            "compare/aggregate_up/files/*.xlsx",
        ]
    },
)
