import json
from datetime import datetime
import pdfkit
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def ensure_directory_exists(directory):
    """Ensure the specified directory exists; create it if it doesn't."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")

def generate_html_file(advisory_data, template_html_original):
    """
    Generate an HTML file from a given advisory data and template string.
    Returns the name of the generated HTML file.
    """
    try:
        # 1. Make a fresh copy of the template HTML
        template_html = template_html_original

        # 2. Prepare placeholders
        placeholders = {
            "{{AdvisoryID}}": advisory_data.get("AdvisoryID", ""),
            "{{Scope}}":      advisory_data.get("Scope", ""),
            "{{Severity}}":   advisory_data.get("Severity", ""),
            "{{CVSS}}":       advisory_data.get("CVSS", ""),
            "{{Date}}":       datetime.now().strftime("%Y-%m-%d"),
            "{{Year}}":       str(datetime.now().year)
        }

        # 3. Replace placeholders
        for placeholder, value in placeholders.items():
            template_html = template_html.replace(placeholder, value)

        # 4. Determine the output HTML filename
        advisory_id = advisory_data.get("AdvisoryID", "NoID")
        filename = advisory_id.replace("/", "_")
        html_filename = f"{filename}.html"

        # 5. Ensure the 'html' directory exists
        ensure_directory_exists("html")

        # 6. Write to file
        with open(f"html/{html_filename}", "w", encoding="utf-8") as out_html:
            out_html.write(template_html)

        logging.info(f"Generated HTML file: {html_filename}")
        return html_filename

    except Exception as e:
        logging.error(f"Error generating HTML file: {e}")
        return None

def convert_html_to_pdf(html_filename):
    """
    Convert an existing HTML file to a PDF in A4 size using pdfkit.
    Returns the name of the generated PDF file.
    """
    try:
        # 1. Build the PDF file name from the HTML file name
        pdf_filename = html_filename.replace(".html", ".pdf")

        # 2. Ensure the 'pdf' directory exists
        ensure_directory_exists("contexts")

        # 3. Set pdfkit options to produce A4 size PDF
        pdf_options = {
            'page-size': 'A4',
            'margin-top': '0.0in',
            'margin-right': '0.0in',
            'margin-bottom': '0.0in',
            'margin-left': '0.0in',
            'encoding': 'UTF-8',
            'dpi': '96',
            'zoom': '2.0',
        }

        # 4. Convert using pdfkit
        pdfkit.from_file(f"html/{html_filename}", f"contexts/{pdf_filename}", options=pdf_options)

        logging.info(f"Converted {html_filename} to PDF: {pdf_filename}")
        return pdf_filename

    except Exception as e:
        logging.error(f"Error converting HTML to PDF: {e}")
        return None

def main():
    try:
        # 1. Load the list of advisories from JSON
        with open("data.json", "r", encoding="utf-8") as f:
            advisories = json.load(f)

        # 2. Read the HTML template
        with open("templates/cover-template.html", "r", encoding="utf-8") as f:
            template_html_original = f.read()

        # 3. Loop over each advisory and generate both HTML and PDF
        for advisory_data in advisories["Advisories"]:
            # Generate HTML file
            html_file = generate_html_file(advisory_data, template_html_original)

            if html_file:
                # Convert that HTML to PDF (A4 size)
                convert_html_to_pdf(html_file)

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()