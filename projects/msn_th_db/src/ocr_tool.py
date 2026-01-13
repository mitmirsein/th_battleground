
import fitz  # PyMuPDF
import sys
import subprocess
from pathlib import Path
import os
import traceback

def ocr_pdf(pdf_path: Path, output_txt_path: Path, max_pages: int = None):
    print(f"Opening PDF: {pdf_path}", flush=True)
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Failed to open PDF: {e}", flush=True)
        return

    total_pages = len(doc)
    if max_pages and max_pages < total_pages:
        print(f"Limiting to first {max_pages} pages.", flush=True)
        total_pages = max_pages

    full_text = ""
    print(f"Processing {pdf_path.name} with {total_pages} pages...", flush=True)
    
    for page_num in range(total_pages):
        try:
            page = doc[page_num]
            
            # Render page to image
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")
            
            # Call tesseract
            cmd = ['tesseract', 'stdin', 'stdout', '-l', 'deu+eng+grc+heb']
            
            process = subprocess.run(
                cmd,
                input=img_bytes,
                capture_output=True,
                check=False
            )
            
            if process.returncode != 0:
                print(f"Error on page {page_num}: {process.stderr.decode()}", flush=True)
                continue
                
            page_text = process.stdout.decode('utf-8')
            full_text += f"\n\n--- Page {page_num} ---\n\n"
            full_text += page_text
            
            print(f"  Page {page_num + 1}/{total_pages} processed ({len(page_text)} chars)", flush=True)
            
        except Exception as e:
            print(f"Exception on page {page_num}: {e}", flush=True)
            traceback.print_exc()
            
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(full_text)
        
    print(f"Saved OCR text to {output_txt_path}", flush=True)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ocr_tool.py <input_pdf> <output_txt> [max_pages]", flush=True)
        sys.exit(1)
    
    max_p = int(sys.argv[3]) if len(sys.argv) > 3 else None
    ocr_pdf(Path(sys.argv[1]), Path(sys.argv[2]), max_p)
