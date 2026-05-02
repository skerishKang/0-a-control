#!/usr/bin/env python3
"""
Script to extract the complete text of "The Golden Flood" by Edwin Lefevre 
from the HTML file, removing all HTML tags and Project Gutenberg metadata.
"""

import re
from bs4 import BeautifulSoup

def clean_text(text):
    """Clean up text by removing HTML entities and normalizing whitespace."""
    # Replace HTML entities
    text = text.replace('&ldquo;', '"')
    text = text.replace('&rdquo;', '"')
    text = text.replace('&rsquo;', "'")
    text = text.replace('&mdash;', "—")
    text = text.replace('&amp;', "&")
    text = text.replace('&lsquo;', "'")
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def extract_novel_content(html_file, output_file):
    """Extract the novel content from HTML file."""
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find content between part headers
    part_one_start = content.find('PART ONE: THE FLOOD')
    part_two_start = content.find('PART TWO: THE GOLD')
    part_three_start = content.find('PART III: THE PARADOXICAL PANIC')
    end_marker = content.find('*** END OF THE PROJECT GUTENBERG EBOOK')
    
    print(f"Part One starts at: {part_one_start}")
    print(f"Part Two starts at: {part_two_start}")
    print(f"Part Three starts at: {part_three_start}")
    print(f"End marker at: {end_marker}")
    
    # Extract each part
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("THE GOLDEN FLOOD\n")
        out.write("By Edwin Lefevre\n\n")
        out.write("="*60 + "\n")
        
        # Extract Part One
        out.write("PART ONE: THE FLOOD\n")
        out.write("="*60 + "\n\n")
        
        part_one_html = content[part_one_start:part_two_start]
        part_one_soup = BeautifulSoup(part_one_html, 'html.parser')
        
        paragraphs = part_one_soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and not text.startswith('PART'):
                cleaned = clean_text(text)
                if cleaned:
                    out.write(cleaned + "\n\n")
        
        # Extract Part Two
        out.write("\n" + "="*60 + "\n")
        out.write("PART TWO: THE GOLD\n")
        out.write("="*60 + "\n\n")
        
        part_two_html = content[part_two_start:part_three_start]
        part_two_soup = BeautifulSoup(part_two_html, 'html.parser')
        
        paragraphs = part_two_soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and not text.startswith('PART'):
                cleaned = clean_text(text)
                if cleaned:
                    out.write(cleaned + "\n\n")
        
        # Extract Part Three
        out.write("\n" + "="*60 + "\n")
        out.write("PART III: THE PARADOXICAL PANIC\n")
        out.write("="*60 + "\n\n")
        
        part_three_html = content[part_three_start:end_marker]
        part_three_soup = BeautifulSoup(part_three_html, 'html.parser')
        
        paragraphs = part_three_soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and not text.startswith('PART') and not text.startswith('***'):
                cleaned = clean_text(text)
                if cleaned:
                    out.write(cleaned + "\n\n")

if __name__ == "__main__":
    html_file = r'G:\Ddrive\BatangD\task\workdiary\5. 공부및일지\고전\The_Golden_Flood\golden_flood.html'
    output_file = r'G:\Ddrive\BatangD\task\workdiary\5. 공부및일지\고전\The_Golden_Flood\golden_flood_complete.txt'
    
    extract_novel_content(html_file, output_file)
    print(f"Novel extraction complete! Output saved to: {output_file}")