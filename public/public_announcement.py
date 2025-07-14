import json
import yaml
from datetime import datetime
from string import Template


# Configurable path prefix for the YAML and MD files
PATH_PREFIX = "security-announcements/security-advisories/2025/"
BASE_PATH_PLACEHOLDER = "{{#base_path#}}"

# Function to read a file
def read_file(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None

# Function to generate markdown content
def generate_markdown(data, template):
    # Add system date and version to the data
    data["date"] = datetime.now().strftime("%Y-%m-%d")
    data["version"] = "1.0.0"  # Replace with your desired version or logic

    # Dynamically generate the Affected Products list
    if "Products" in data and data["Products"]:
        data["Products"] = "\n* ".join(data["Products"])
    else:
        data["Products"] = "No affected products listed."

    # Conditionally replace the Community Users subsection if PR is empty or contains only empty strings
    if "PR" not in data or not any(data["PR"]):
        # Replace the Community Users subsection with the default message
        template = template.replace(
            "Apply the relevant fixes to your product using the public fix(es) provided below.\n\n* $PR\n\nIf applying the fix or update is not feasible, migrate to the latest unaffected version of the respective WSO2 product(s).\n",
            "We highly recommend to migrate to the latest version of respective WSO2 products to mitigate the identified vulnerabilities.\n"
        )
    else:
        # Convert PR list to markdown links, filtering out empty strings
        data["PR"] = "\n* ".join([f"[{pr}]({pr})" for pr in data["PR"] if pr])
    
    # Conditionally include the Credits section
    if "Credits" not in data or not data["Credits"]:
        # Remove the Credits section from the template
        template = template.replace("### CREDITS\nWSO2 thanks, **$Credits** for responsibly reporting the identified issue and working with us as we addressed it.", "")
    
    # Conditionally include the referance section
    if "References" not in data or not data["References"]:
        # Remove the referance section from the template
        template = template.replace("### REFERENCES\n* $References", "")
    else:
        # Add refernce links
        data["References"] = "\n* ".join([f"[{References}]({References})" for References in data["References"] if References])

    # Substitute placeholders with data
    markdown_output = Template(template).substitute(data)

    return markdown_output

# Function to sanitize the title for filename
def sanitize_title(title):
    # Remove the "CVE" part and any trailing slashes or colons
    return title.split("/")[0].replace(":", "_").strip()

# Save markdown content to a file
def save_markdown_file(title, content):
    # Sanitize the title to create a valid filename
    filename = sanitize_title(title) + ".md"
    with open(filename, "w") as file:
        file.write(content)
    print(f"Markdown file '{filename}' created successfully.")
    return filename

# Function to generate YAML file with markdown file paths
def generate_yaml_file(file_mapping, yaml_file_path):
    # Convert the file mapping to the required YAML format
    yaml_data = [{k: v + ".md"} for k, v in file_mapping.items()]
    
    # Write the YAML data to the file with single quotes
    with open(yaml_file_path, "w") as file:
        file.write("---\n")
        for item in yaml_data:
            for key, value in item.items():
                file.write(f"- '{key}': '{value}'\n")
    print(f"YAML file '{yaml_file_path}' created successfully.")

# Function to generate a markdown file with links to all advisories
def generate_advisory_list(file_mapping, md_file_path):
    # Generate the markdown content
    md_content = "\n".join([f"* [{title}]({BASE_PATH_PLACEHOLDER}/{path})" for title, path in file_mapping.items()])
    
    # Write the markdown content to the file
    with open(md_file_path, "w") as file:
        file.write(md_content)
    print(f"Advisory list markdown file '{md_file_path}' created successfully.")

# Main function
def main():
    # Path to the JSON file
    json_file_path = "data.json"  # Replace with your JSON file path

    # Path to the template file
    template_file_path = "template.md"  # Replace with your template file path

    # Path to the output YAML file
    yaml_file_path = "file_mapping.yaml"  # Replace with your desired YAML file path

    # Path to the output advisory list markdown file
    advisory_list_file_path = "advisory_list.md"  # Replace with your desired MD file path

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

    # Check if JSON data is a list
    if not isinstance(json_data, list):
        print("Error: JSON data should be a list of objects.")
        return

    # Read template
    template = read_file(template_file_path)
    if template is None:
        return

    # Dictionary to store file mappings for the YAML file
    file_mapping = {}

    # Generate markdown files for each unique Title
    for data in json_data:
        if "Title" not in data:
            print("Error: Missing 'Title' field in JSON data.")
            continue

        # Generate markdown content
        markdown_content = generate_markdown(data, template)

        # Save markdown content to a file
        filename = save_markdown_file(data["Title"], markdown_content)

        # Add the file mapping to the dictionary
        file_mapping[data["Title"].split("/")[0]] = PATH_PREFIX + filename.split('.')[0]

    # Generate the YAML file with file mappings
    generate_yaml_file(file_mapping, yaml_file_path)

    # Generate the advisory list markdown file
    generate_advisory_list(file_mapping, advisory_list_file_path)

# Run the script
if __name__ == "__main__":
    main()