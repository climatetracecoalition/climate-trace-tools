from setuptools import setup

setup(
    name="climate_trace_tools",
    version="0.0.1",
    description="tools for comparing climate trace data to other data sources",
    author="Christy Lewis",
    author_email="christy@watttime.org",
    install_requires=[
        "numpy",
        "pandas",
        "plotly",
    ],
    include_package_data={
        "climate_trace_tools": [
            "data/country/*.zip",
            "data/source/*.zip",
            "data/supplementary/*.zip",
            "compare/subtract_out/files/*.csv",
            "compare/subtract_out/files/*.xlsx",
            "compare.aggregate_up/files/*.xlsx",
        ]
    },
)
