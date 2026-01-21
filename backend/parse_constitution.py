import PyPDF2
import json
import re

def parse_constitution():
    pdf_path = 'constitution.pdf'
    json_path = 'constitution.json'
    
    parts = []
    current_part = {"id": "PREAMBLE", "title": "Preamble", "articles": []}
    current_article = None
    
    # Regex patterns (adjusted for likely PDF text output)
    part_pattern = re.compile(r'^\s*PART\s+([IVX]+)', re.IGNORECASE)
    # Article pattern often appears as "1. Name of..." or "Article 1" depending on extraction
    # The Indian Constitution PDF usually has "Article 1" or just number on the side.
    # Let's try to detect standard Article headers.
    article_pattern = re.compile(r'^\s*(\d+[A-Z]?)\.\s+(.*)') 

    full_text = ""

    print("Reading PDF...")
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return

    print(f"Extracted {len(full_text)} characters. Parsing...")
    
    lines = full_text.split('\n')
    
    # Heuristic parsing
    # We will assume a simple state machine
    
    # Initialize with Preamble
    parts.append(current_part)
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for Part
        part_match = part_pattern.match(line)
        if part_match:
            # New Part
            part_id = f"PART_{part_match.group(1)}"
            current_part = {
                "id": part_id,
                "title": line, # capture full line like "PART III FUNDAMENTAL RIGHTS"
                "articles": []
            }
            parts.append(current_part)
            current_article = None
            continue
            
        # Check for Article Start (e.g., "14. Equality before law.")
        # Note: PyPDF2 might extract it as "14. \n Equality..." or "14. Equality..."
        art_match = article_pattern.match(line)
        if art_match:
            art_num = art_match.group(1)
            art_title = art_match.group(2)
            
            # Simple validity check to avoid list items being mistaken for articles
            # Articles usually are sequential, but checking that is hard.
            # Let's assume if it starts with Digits + Dot, it's an article candidate
            
            # Create new article
            current_article = {
                "id": art_num,
                "title": art_title,
                "content": ""
            }
            current_part["articles"].append(current_article)
            continue
        
        # If we have a current article, append text to it
        if current_article:
            current_article["content"] += line + " "
        elif current_part["id"] == "PREAMBLE":
            # Append to preamble content (using a dummy article for preamble/intro text)
            if not current_part["articles"]:
                current_part["articles"].append({"id": "PREAMBLE", "title": "The Preamble", "content": ""})
            current_part["articles"][0]["content"] += line + " "

    # Clean up content
    for part in parts:
        for art in part["articles"]:
            art["content"] = art["content"].strip()

    # Filter empty parts
    parts = [p for p in parts if p["articles"]]

    output = {"parts": parts}
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"Successfully created {json_path} with {len(parts)} parts.")

if __name__ == "__main__":
    parse_constitution()
