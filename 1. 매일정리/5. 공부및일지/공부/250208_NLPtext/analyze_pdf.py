import fitz
import sys
import os

def analyze(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return

    doc = fitz.open(pdf_path)
    print(f"File: {os.path.basename(pdf_path)}")
    print(f"Pages: {len(doc)}")
    
    # Extract first page as sample
    page = doc[0]
    text = page.get_text()
    print("\n--- FIRST PAGE PREVIEW ---")
    print(text[:1000] + "..." if len(text) > 1000 else text)
    
    # Check for images/tables (roughly)
    img_count = len(page.get_images())
    print(f"\nImages on page 1: {img_count}")

if __name__ == "__main__":
    path = r"G:\Ddrive\BatangD\task\workdiary\1. 매일정리\5. 공부및일지\공부\250208_NLPtext\2. Regular Expressions, Text Normalization, Edit Distance.pdf"
    analyze(path)
