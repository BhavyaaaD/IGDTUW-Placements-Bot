import pdfplumber

def extract_text_from_pdf(pdf_path, output_txt_file=None):
    """
    Extracts text from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.
        output_txt_file (str, optional): Path to save extracted text.

    Returns:
        str: Extracted text from the PDF.
    """
    extracted_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text += page.extract_text() + "\n"

    if output_txt_file:
        with open(output_txt_file, "w", encoding="utf-8") as f:
            f.write(extracted_text)
        print(f"Extracted text saved to {output_txt_file}")

    return extracted_text

# Example Usage
pdf_path = "C:/Users/bhavy/Langchain/Langchain_basics/Data/Tnp_Brochure_2022-23.pdf" 
output_txt_file = "C:/Users/bhavy/Langchain/Langchain_basics/Data/text_output.txt"  

extracted_text = extract_text_from_pdf(pdf_path, output_txt_file)
print("Extracted Text Preview:\n", extracted_text[:500])  # Print first 500 characters
