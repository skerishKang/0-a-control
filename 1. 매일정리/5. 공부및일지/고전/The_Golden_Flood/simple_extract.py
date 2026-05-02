import re

# Read the HTML file
with open(r'G:\Ddrive\BatangD\task\workdiary\5. 공부및일지\고전\The_Golden_Flood\golden_flood.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the three parts
part1_start = content.find('PART ONE: THE FLOOD')
part2_start = content.find('PART TWO: THE GOLD') 
part3_start = content.find('PART III: THE PARADOXICAL PANIC')
end_pos = content.find('*** END OF THE PROJECT GUTENBERG EBOOK')

print(f"Part positions: {part1_start}, {part2_start}, {part3_start}, {end_pos}")

# Extract text and clean it up
def clean_html_text(html_segment):
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_segment)
    # Clean up HTML entities
    text = text.replace('&ldquo;', '"')
    text = text.replace('&rdquo;', '"') 
    text = text.replace('&rsquo;', "'")
    text = text.replace('&mdash;', "—")
    text = text.replace('&amp;', "&")
    text = text.replace('&lsquo;', "'")
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    # Split into paragraphs
    paragraphs = text.split('\n')
    clean_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if p and len(p) > 10 and not p.startswith('PART'):
            clean_paragraphs.append(p)
    return clean_paragraphs

# Extract each part
part1_html = content[part1_start:part2_start]
part2_html = content[part2_start:part3_start] 
part3_html = content[part3_start:end_pos]

part1_text = clean_html_text(part1_html)
part2_text = clean_html_text(part2_html)
part3_text = clean_html_text(part3_html)

# Write output
with open(r'G:\Ddrive\BatangD\task\workdiary\5. 공부및일지\고전\The_Golden_Flood\golden_flood_extracted_complete.txt', 'w', encoding='utf-8') as out:
    out.write("THE GOLDEN FLOOD\n")
    out.write("By Edwin Lefevre\n\n")
    out.write("="*60 + "\n")
    out.write("PART ONE: THE FLOOD\n") 
    out.write("="*60 + "\n\n")
    
    for para in part1_text:
        out.write(para + "\n\n")
    
    out.write("\n" + "="*60 + "\n")
    out.write("PART TWO: THE GOLD\n")
    out.write("="*60 + "\n\n")
    
    for para in part2_text:
        out.write(para + "\n\n")
        
    out.write("\n" + "="*60 + "\n")
    out.write("PART III: THE PARADOXICAL PANIC\n")
    out.write("="*60 + "\n\n")
    
    for para in part3_text:
        out.write(para + "\n\n")

print("Extraction complete!")