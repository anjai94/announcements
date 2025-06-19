import json
import os
from jinja2 import Environment, FileSystemLoader

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load the JSON data
data_path = os.path.join(script_dir, 'data.json')
with open(data_path, 'r') as file:
    data = json.load(file)

# Extract the month, year, and base URL from the JSON data
month = data.get('Month', 'UnknownMonth')
year = data.get('Year', 'UnknownYear')
base_url = data.get('BaseUrl', '')

# Prepare the data for the template
data_list = []
for advisory in data['Advisories']:
    # Replace "/" with "_" in AdvisoryID
    advisory_id = advisory['AdvisoryID'].replace("/", "_")
    download_link = f"{base_url}{year}/{month}/{advisory_id}.pdf"
    advisory['DownloadLink'] = download_link
    data_list.append(advisory)

# Load the HTML template
template_dir = os.path.join(script_dir, 'templates')
env = Environment(loader=FileSystemLoader(template_dir))
template = env.get_template('sn-template.html')

# Render the template with the data
rendered_html = template.render(data_list=data_list)

# Create the output file name using the extracted month and year
output_filename = f"WSO2 Security Bulletin Summary for {month} {year}.html"

# Save the rendered HTML to the dynamically named file
output_path = os.path.join(script_dir, output_filename)
with open(output_path, 'w') as file:
    file.write(rendered_html)

print(f"HTML file has been generated as '{output_filename}'")