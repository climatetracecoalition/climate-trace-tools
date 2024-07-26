from setuptools import setup

setup(
    name = "climate_trace_tools",
    version = '0.0.1',
    description = 'tools for comparing climate trace data to other data sources',
    author = 'Christy Lewis',
    author_email = 'christy@watttime.org',
    install_requires = [
        'numpy',
        'pandas',
        'os',
        'plotly',
        'json',
        'copy',
        ],
    include_package_data=True
    )
