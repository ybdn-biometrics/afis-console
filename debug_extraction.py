import os
import fitz
import re

def extract_identities_info(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    
    text_lower = text.lower()
    
    # Pattern for count
    # We use finditer to iterate through all matches
    # Capture the value
    pattern_count = r"nombre\s+d[’']homonymes\s*[:\s]\s*(\d+)"
    
    matches = list(re.finditer(pattern_count, text_lower))
    
    identities = []
    
    # We also need to find "né(e) le" positions to infer blocks
    # But "né(e) le" detection might be tricky if formatting varies.
    # Alternatively, we just take the X lines before the match.
    
    lines = text.split('\n')
    
    # Let's try to map generic text positions to lines for better extraction
    # Actually, working with the full string index is easier with regex match objects
    
    last_pos = 0
    for m in matches:
        count = int(m.group(1))
        start_pos = m.start()
        
        # Look backwards for "né(e) le"
        # We search from last_pos to start_pos
        # But we want the *closest* "né(e) le" before start_pos
        subtext = text_lower[last_pos:start_pos]
        
        # Find all "né(e) le" in subtext
        ne_le_matches = list(re.finditer(r"né\(e\)\s+le", subtext))
        
        alias_name = "Inconnu"
        if ne_le_matches:
            # The start of the block for this identity
            block_start_rel = ne_le_matches[-1].start()
            block_start_abs = last_pos + block_start_rel
            
            # The alias is likely between "né(e) le date" and "nombre de signalisations" or just after availability
            # Let's just grab the text chunk between "né(e) le" and the count pattern, clean it up
            
            chunk = text[block_start_abs:start_pos]
            # Clean up newlines and extra spaces
            #chunk = " ".join(chunk.split())
            
            # Try to extract name roughly. 
            # Often formatting is: 
            # Né(e) le DD/MM/YYYY
            # NAME Firstname
            # ...
            
            lines_in_chunk = chunk.split('\n')
            # Filter empty lines
            lines_in_chunk = [l.strip() for l in lines_in_chunk if l.strip()]
            
            # Line 0 is usually "Né(e) le ..."
            # Line 1 might be the name
            if len(lines_in_chunk) > 1:
                possible_name = lines_in_chunk[1]
                # Avoid capturing technical lines if layout shifts
                if "signalisation" not in possible_name.lower():
                     alias_name = possible_name
            
        identities.append({
            'alias': alias_name,
            'homonym_count': count
        })
        
        last_pos = start_pos + len(m.group(0))

    return identities

folder = "/Users/ybdn/dev/afis-console/tests/EXEMPLES_RAPPORTS"
count = 0
for filename in os.listdir(folder):
    if filename.endswith(".pdf"):
        path = os.path.join(folder, filename)
        print(f"--- {filename} ---")
        identities = extract_identities_info(path)
        for i in identities:
            print(f"  Alias: {i['alias']} | Count: {i['homonym_count']}")
        count += 1
        if count >= 5: break
