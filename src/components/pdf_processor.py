import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_file):
    """
    Extrai o texto de um arquivo PDF.
    """
    try:
        # Abre o PDF diretamente do stream de bytes
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        # Extrai o texto da primeira (e única) página
        text = ""
        for page in pdf_document:
            text += page.get_text()
            
        return text
    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")
        return None
