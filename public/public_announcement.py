import json
import yaml
from datetime import datetime
from string import Template

# Configurable path prefix for the YAML and MD files
PATH_PREFIX = "security-announcements/security-advisories/"
BASE_PATH_PLACEHOLDER = "{{#base_path#}}"

# Function to read a file
def read_file(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None

# Function to generate markdown content with safe substitution
def generate_markdown(data, template):
    # Add system date and version to the data
    data["date"] = datetime.now().strftime("%Y-%m-%d")
    data["version"] = "1.0.0"

    # Extract CVE ID from AdvisoryID if it exists
    advisory_id = data.get("AdvisoryID", "")
    if "/" in advisory_id:
        data["CVEID"] = advisory_id.split("/")[1]
    else:
        template = template.replace('<p class="doc-info">CVE IDs: <a href="https://www.cve.org/CVERecord?id=$CVEID">$CVEID</a></p>\n', "")

    # Conditionally replace the Community Users subsection if PR is empty or placeholder
    pr_value = data.get("PR", "")
    if not pr_value:
        # Replace the Community Users subsection with the default message
        template = template.replace(
            "#### Community Users (Open Source)\nApply the relevant fixes to your product using the public fix(es) provided below.\n\n* $PR\n\nIf applying the fix or update is not feasible, migrate to the latest unaffected version of the respective WSO2 product(s).",
            "#### Community Users (Open Source)\nWe highly recommend to migrate to the latest version of respective WSO2 products to mitigate the identified vulnerabilities."
        )
    else:
        # Convert PR list to markdown links, filtering out empty strings
        data["PR"] = "\n* ".join([f"[{pr}]({pr})" for pr in data["PR"] if pr])

    # Safe template substitution
    class SafeTemplate(Template):
        def substitute(self, mapping):
            # Handle missing keys by providing empty strings
            def convert(mo):
                named = mo.group('named')
                if named is not None:
                    return str(mapping.get(named, ''))
                return mo.group()
            
            return self.pattern.sub(convert, self.template)

    # Substitute placeholders with data safely
    markdown_output = SafeTemplate(template).substitute(data)
    return markdown_output

# Function to sanitize the AdvisoryID for filename
def sanitize_AdvisoryID(AdvisoryID):
    return AdvisoryID.split("/")[0].replace(":", "_").replace("/", "_").strip()

# Function to extract year from AdvisoryID
def extract_year_from_advisory_id(advisory_id):
    # Extract year from AdvisoryID (e.g., "WSO2-2025-4486" -> "2025")
    parts = advisory_id.split('-')
    for part in parts:
        if part.isdigit() and len(part) == 4:  # Look for a 4-digit year
            return part
    # Fallback to current year if no year found
    return datetime.now().strftime("%Y")

# Save markdown content to a file
def save_markdown_file(AdvisoryID, content):
    filename = sanitize_AdvisoryID(AdvisoryID) + ".md"
    with open(filename, "w") as file:
        file.write(content)
    print(f"Markdown file '{filename}' created successfully.")
    return filename

# Function to generate YAML file with markdown file paths
def generate_yaml_file(file_mapping, yaml_file_path):
    # Convert the file mapping to the required YAML format
    yaml_data = [{k: v} for k, v in file_mapping.items()]
    
    # Write the YAML data to the file with single quotes
    with open(yaml_file_path, "w") as file:
        for item in yaml_data:
            for key, value in item.items():
                file.write(f"- '{key}': '{value}'\n")
    print(f"YAML file '{yaml_file_path}' created successfully.")

# Function to generate a markdown file with links to all advisories
def generate_advisory_list(file_mapping, md_file_path):
    # Generate the markdown content
    md_content = "\n".join([f"* [{advisory_id}]({BASE_PATH_PLACEHOLDER}/{path})" for advisory_id, path in file_mapping.items()])
    
    # Write the markdown content to the file
    with open(md_file_path, "w") as file:
        file.write(md_content)
    print(f"Advisory list markdown file '{md_file_path}' created successfully.")

# Main function
def main():
    # Path to the JSON file
    json_file_path = "data.json"

    # Path to the template file
    template_file_path = "template.md"

    # Path to the output YAML file
    yaml_file_path = "file_mapping.yaml"

    # Path to the output advisory list markdown file
    advisory_list_file_path = "advisory_list.md"

    # Read JSON data
    json_data = read_file(json_file_path)
    if json_data is None:
        return

    # Parse JSON data
    try:
        json_data = json.loads(json_data)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{json_file_path}'.")
        return

    # Check if JSON data is a dictionary and contains Advisories
    if not isinstance(json_data, dict):
        print("Error: JSON data should be a dictionary.")
        return

    if "Advisories" not in json_data:
        print("Error: JSON data should contain an 'Advisories' field.")
        return

    if not isinstance(json_data["Advisories"], list):
        print("Error: 'Advisories' field should be a list.")
        return

    # Read template
    template = read_file(template_file_path)
    if template is None:
        return

    # Dictionary to store file mappings for the YAML file
    file_mapping = {}

    # Generate markdown files for each advisory in the Advisories list
    for data in json_data["Advisories"]:
        if "AdvisoryID" not in data:
            print("Error: Missing 'AdvisoryID' field in advisory data.")
            continue

        # Generate markdown content
        markdown_content = generate_markdown(data, template)

        # Save markdown content to a file
        filename = save_markdown_file(data["AdvisoryID"], markdown_content)

        # Extract year from AdvisoryID and create file mapping
        advisory_key = data["AdvisoryID"].split("/")[0]
        year = extract_year_from_advisory_id(advisory_key)
        file_mapping[advisory_key] = f"{PATH_PREFIX}{year}/{advisory_key}"

    # Generate the YAML file with file mappings
    generate_yaml_file(file_mapping, yaml_file_path)

    # Generate the advisory list markdown file
    generate_advisory_list(file_mapping, advisory_list_file_path)

# Run the script
if __name__ == "__main__":
    main()