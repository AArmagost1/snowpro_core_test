import PyPDF2
from pathlib import Path

# Open the PDF
pdf_path = Path("SnowPro Core Test Prep.pdf")

if not pdf_path.exists():
    print("Error: PDF file not found!")
    exit(1)

print(f"Reading {pdf_path}...")

# Extract text from all pages
text = ""
with open(pdf_path, 'rb') as file:
    pdf_reader = PyPDF2.PdfReader(file)
    total_pages = len(pdf_reader.pages)
    
    print(f"Found {total_pages} pages")
    
    for page_num in range(total_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
        
        if (page_num + 1) % 10 == 0:
            print(f"  Processed {page_num + 1}/{total_pages} pages...")

# Save to text file
output_path = Path("snowpro_raw.txt")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(text)

print(f"\n✅ Saved text to {output_path}")
print(f"   Total characters: {len(text):,}")