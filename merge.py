import PyPDF2
import os

def merge_pdfs(input_folder, output_filename):
    merger = PyPDF2.PdfMerger()
    
    # List files and sort them alphabetically
    files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]
    files.sort()
    
    print(f"Found {len(files)} PDFs. Merging...")

    for filename in files:
        path = os.path.join(input_folder, filename)
        merger.append(path)
        print(f"Added: {filename}")

    merger.write(output_filename)
    merger.close()
    print(f"Success! Merged file saved as: {output_filename}")

# Usage
merge_pdfs('./my_pdfs', 'Proof_of_sufficient_financial_resources.pdf')