import PyPDF2

#BROKEN FUNCTION: DOESN'T RETURN ALL TEXT FRO PDF
def pdf2text_fast(path: str) -> str:
    
    """Function to convert pdf to text faster than pdfminer
    
       path: the path to pdf file

       return: text version of pdf document
    """
    
    with open(path, 'rb') as f:
        doc = PyPDF2.PdfFileReader(f)
        text = ''.join([doc.getPage(t).extractText()+'\x0c' for t in range(doc.numPages)])
    return text
