import pandas as pd
import json

# Specify the path to the XLSX file with the comparison dictionaries. For consistency
# download the XLSX from here: https://docs.google.com/spreadsheets/d/1crBeTIm7isN5EkvLbmkhoZYJqep1xzNwDVNnIu94l6E/edit#gid=0
# and then put it in the spreadsheets directory within this directory
xlsx_file_path = 'files/subtract-out-csv-crosswalks.xlsx'
# Define the list of tabs in your XLSX (assuming each tab corresponds to a separate sheet)
tabs = ['unfccc-subtract-out', 'edgar-subtract-out', 'cait-subtract-out', 'pik-tp-subtract-out', 'faostat-subtract-out']

inventory_titles = {
  'climate-trace': 'ClimateTRACE',
  'unfccc_annex_1': 'UNFCCC',
  'unfccc_non_annex_1': 'UNFCCC',
  'edgar': 'EDGAR',
  'cait': 'CAIT',
  'pik-tp': 'PIK',
  'carbon-monitor': 'Carbon Monitor',
  'faostat': 'FAOSTAT'
}

inventory_codes = {
  'unfccc-subtract-out': 'unfccc',
  'edgar-subtract-out': 'edgar',
  'cait-subtract-out': 'cait',
  'pik-tp-subtract-out': 'pik-tp',
  'faostat-subtract-out': 'faostat'
}

def create_sector_title(raw_string):
  formatted_string = raw_string.replace('-', ' ')

  # Capitalize words in the title
  formatted_string = formatted_string.title()

  return formatted_string


def generate_master_dicts():
  # Initialize JSON objects for Annex 1 and Non-Annex 1 data
  annex1_data = {}
  non_annex1_data = {}

  for tab_name in tabs:
      # Read the XLSX file for the current tab
      df = pd.read_excel(xlsx_file_path, sheet_name=tab_name)
      df = df.dropna()
      inventory_code = inventory_codes[tab_name]

      for index, row in df.iterrows():
        annex_1 = row['Annex 1?']
        climate_trace_sector = row['Climate TRACE Sector']
        inventory = row['Inventory']
        sector = row['Sector']
        value = int(row['Value'])
        if sector != 'NaN':
          if annex_1:
            if climate_trace_sector not in annex1_data:
              annex1_data[climate_trace_sector] = {}
            if inventory_code not in annex1_data[climate_trace_sector]:
              annex1_data[climate_trace_sector][inventory_code] = {}
            if inventory not in annex1_data[climate_trace_sector][inventory_code]:
              annex1_data[climate_trace_sector][inventory_code][inventory] = []
            annex1_data[climate_trace_sector][inventory_code][inventory].append((sector, value))
          else:
            if climate_trace_sector not in non_annex1_data:
              non_annex1_data[climate_trace_sector] = {}
            if inventory_code not in non_annex1_data[climate_trace_sector]:
              non_annex1_data[climate_trace_sector][inventory_code] = {}
            if inventory not in non_annex1_data[climate_trace_sector][inventory_code]:
              non_annex1_data[climate_trace_sector][inventory_code][inventory] = []
            non_annex1_data[climate_trace_sector][inventory_code][inventory].append((sector, value))

  # Convert the dictionaries to JSON
  # Print or save the JSON objects as needed

  with open('files/master_comparison_dict_annex1.json', 'w') as f:
    f.write(json.dumps(annex1_data, indent=2))

  with open('files/master_comparison_dict_nonannex1.json', 'w') as f:
    f.write(json.dumps(non_annex1_data, indent=2))


def generate_title_dicts():
  # Initialize JSON objects for Annex 1 and Non-Annex 1 data
  annex1_data = {}
  non_annex1_data = {}

  for tab_name in tabs:
      # Read the XLSX file for the current tab
      df = pd.read_excel(xlsx_file_path, sheet_name=tab_name)
      df = df.dropna()

      for index, row in df.iterrows():
        annex_1 = row['Annex 1?']
        climate_trace_sector = row['Climate TRACE Sector']
        inventory = row['Inventory']
        inventory_title = inventory_titles[inventory]
        sector = row['Sector']
        sector_title = create_sector_title(climate_trace_sector)
        value = int(row['Value'])
        if value > 0:
          value_string = '     + '
        else:
          value_string = '     - '
        if sector != 'NaN':
          if annex_1:
            if climate_trace_sector not in annex1_data:
              annex1_data[climate_trace_sector] = {
                'title': sector_title,
                'legend': {}
              }
            if tab_name not in annex1_data[climate_trace_sector]['legend']:
              annex1_data[climate_trace_sector]['legend'][tab_name] = {}
            if inventory not in annex1_data[climate_trace_sector]['legend'][tab_name]:
              annex1_data[climate_trace_sector]['legend'][tab_name][inventory] = {
                'desc': inventory_title,
                'comps': []
              }
            annex1_data[climate_trace_sector]['legend'][tab_name][inventory]['comps'].append((sector, value_string))
          else:
            if climate_trace_sector not in non_annex1_data:
              non_annex1_data[climate_trace_sector] = {
                'title': sector_title,
                'legend': {}
              }
            if tab_name not in non_annex1_data[climate_trace_sector]['legend']:
              non_annex1_data[climate_trace_sector]['legend'][tab_name] = {}
            if inventory not in non_annex1_data[climate_trace_sector]['legend'][tab_name]:
              non_annex1_data[climate_trace_sector]['legend'][tab_name][inventory] = {
                'desc': inventory_title,
                'comps': []
              }
            non_annex1_data[climate_trace_sector]['legend'][tab_name][inventory]['comps'].append((sector, value_string))

  # Convert the dictionaries to JSON
  # Print or save the JSON objects as needed

  with open('files/title_dict_annex1', 'w') as f:
    f.write(json.dumps(annex1_data, indent=2))

  with open('files/title_dict_nonannex1', 'w') as f:
    f.write(json.dumps(non_annex1_data, indent=2))



if __name__ == '__main__':
    generate_master_dicts()
    generate_title_dicts()