import json
import time
from deep_translator import GoogleTranslator

def translate_blocks(input_json, output_json):
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    translator = GoogleTranslator(source='en', target='ko')
    
    print("Translating pages...")
    for i, page in enumerate(data):
        print(f"Translating Page {page['page']}...")
        for el in page["elements"]:
            if el["type"] == "text":
                content = el["content"].strip()
                if not content:
                    el["ko"] = ""
                    continue
                
                # Replace newlines with spaces for better translation context
                content_for_trans = " ".join(content.split())
                
                try:
                    el["ko"] = translator.translate(content_for_trans)
                    time.sleep(0.1) # Be nice to the API
                except Exception as e:
                    print(f"Translation error: {e}")
                    el["ko"] = "[Translation Error]"
            elif el["type"] == "image":
                el["ko"] = ""
                
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else "visual_extracted.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "translated_visual.json"
    translate_blocks(input_file, output_file)
    print(f"Full JSON {output_file} translated successfully.")
