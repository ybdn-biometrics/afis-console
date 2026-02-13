import os
import fitz

def extract_section_identites(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    
    text_lower = text.lower()
    start_marker = "section / identités"
    if start_marker not in text_lower:
        start_marker = "section/identités"
    
    if start_marker in text_lower:
        start_idx = text_lower.find(start_marker)
        # Try to find the end of the section, maybe "section /" something else or end of page
        # usually sections start with "section /"
        end_idx = text_lower.find("section /", start_idx + len(start_marker))
        
        snippet = text[start_idx:end_idx] if end_idx != -1 else text[start_idx:]
        return snippet
    return None

folder = "/Users/ybdn/dev/afis-console/tests/EXEMPLES_RAPPORTS"
count = 0
for filename in os.listdir(folder):
    if filename.endswith(".pdf"):
        path = os.path.join(folder, filename)
        print(f"--- Analyzing {filename} ---")
        snippet = extract_section_identites(path)
        if snippet:
            print(snippet[:1000]) # First 1000 chars of section
            print("\n" + "="*20 + "\n")
        
        count += 1
        if count >= 3: break
