from docx import Document
from langchain_community.document_loaders import PyMuPDFLoader


def load_resume(file_path):
    """
    Load the content of a CV file.

    Parameters:
    file (str): The path to the CV file.

    Returns:
    str: The content of the CV file.
    """
    loader = PyMuPDFLoader(file_path)
    pages = loader.load()
    page_content = ""
    for page in pages:
        page_content += page.page_content
    return page_content


def write_cover_letter_to_doc(text, filename="temp/cover_letter.docx"):
    """
    Writes the given text as a cover letter to a Word document.

    Parameters:
    text (str): The text content of the cover letter.
    filename (str): The filename and path where the document will be saved. Default is "temp/cover_letter.docx".

    Returns:
    str: The filename and path of the saved document.
    """
    doc = Document()
    paragraphs = text.split("\n")
    # Add each paragraph to the document
    for para in paragraphs:
        doc.add_paragraph(para)
    # Save the document to the specified file
    doc.save(filename)
    return filename
