import pypdf
import sys

pdf_path = r"C:\Users\jmfs2\Downloads\screencapture-utagawakogyo-2026-01-27-14_44_39.pdf"

try:
    reader = pypdf.PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n\n"
    
    print(text)
except Exception as e:
    print(f"Error: {e}")
