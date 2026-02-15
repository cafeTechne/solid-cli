
import os
from pypdf import PdfReader

pdf_files = [
    "2201.07034v1.pdf", "2004.07376v4.pdf", "2404.05317v5.pdf"
]
for pdf_file in pdf_files:
    print(f"\n--- Reading {pdf_file} ---")
    try:
        reader = PdfReader(pdf_file)
        text = ""
        # Read first page only
        if len(reader.pages) > 0:
            text += reader.pages[0].extract_text()
        print(text[:1500]) 
    except Exception as e:
        print(f"Error reading {pdf_file}: {e}")
    except Exception as e:
        print(f"Error reading {pdf_file}: {e}")
