import os
import PyPDF2

def merge_pdfs(input_file1, input_file2, output_file):
    # Open the PDF files in binary mode
    with open(input_file1, 'rb') as file1, open(input_file2, 'rb') as file2:
        # Create PDF reader objects
        pdf_reader1 = PyPDF2.PdfReader(file1)
        pdf_reader2 = PyPDF2.PdfReader(file2)

        # Create PDF writer object
        pdf_writer = PyPDF2.PdfWriter()

        # Add pages from the first PDF
        for page_num in range(len(pdf_reader1.pages)):
            page = pdf_reader1.pages[page_num]
            pdf_writer.add_page(page)

        # Add pages from the second PDF
        for page_num in range(len(pdf_reader2.pages)):
            page = pdf_reader2.pages[page_num]
            pdf_writer.add_page(page)

        # Create the output PDF file in binary write mode
        with open(output_file, 'wb') as output_pdf:
            # Write the merged content to the output PDF file
            pdf_writer.write(output_pdf)

def get_pdf_pairs(input_dir):
    files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
    pairs = []
    processed_files = set()
    
    for file1 in files:
        if file1 in processed_files:
            continue
        file2 = file1.replace('.pdf', '-pdf.pdf')
        if file2 in files:
            pairs.append((file1, file2))
            processed_files.add(file1)
            processed_files.add(file2)
        else:
            print("incorrect file name. Please check both files with same name.")
    return pairs

if __name__ == "__main__":
    input_dir = 'contexts/'
    output_dir = 'advisories/'

    pdf_pairs = get_pdf_pairs(input_dir)
    
    for input_file1, input_file2 in pdf_pairs:
        output_file = os.path.join(output_dir, input_file1)
        merge_pdfs(os.path.join(input_dir, input_file1), os.path.join(input_dir, input_file2), output_file)
        print(f"Merged {input_file1} and {input_file2} into {output_file}")
