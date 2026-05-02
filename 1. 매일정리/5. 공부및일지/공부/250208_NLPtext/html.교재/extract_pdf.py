import fitz
import os
import json

def extract_content(pdf_path, output_img_dir):
    doc = fitz.open(pdf_path)
    content = []
    
    if not os.path.exists(output_img_dir):
        os.makedirs(output_img_dir)

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_content = {
            "page": page_num + 1,
            "elements": []
        }

        # 1. Extract Tables
        tables = page.find_tables()
        table_list = []
        for tab in tables:
            table_list.append({
                "type": "table",
                "data": tab.extract(),
                "bbox": tab.bbox
            })

        # 2. Extract Images
        images = page.get_images(full=True)
        image_list = []
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            img_filename = f"page{page_num+1}_img{img_index+1}.{image_ext}"
            img_path = os.path.join(output_img_dir, img_filename)
            with open(img_path, "wb") as f:
                f.write(image_bytes)
            
            # Find image location (approximate)
            img_info = page.get_image_info(xrefs=True)
            bbox = None
            for info in img_info:
                if info['xref'] == xref:
                    bbox = info['bbox']
                    break
            
            image_list.append({
                "type": "image",
                "src": f"images/{img_filename}",
                "bbox": bbox
            })

        # 3. Extract Text Blocks
        blocks = page.get_text("blocks")
        for b in blocks:
            # Check if block overlaps with tables (skip text inside tables if redundant)
            is_in_table = False
            for tab in table_list:
                if fitz.Rect(b[:4]).intersects(fitz.Rect(tab["bbox"])):
                    is_in_table = True
                    break
            
            if not is_in_table:
                text = b[4].strip()
                if text:
                    page_content["elements"].append({
                        "type": "text",
                        "content": text,
                        "bbox": b[:4]
                    })

        # Add tables and images to elements, sort by vertical position (y0)
        page_content["elements"].extend(table_list)
        page_content["elements"].extend(image_list)
        page_content["elements"].sort(key=lambda x: x["bbox"][1] if x["bbox"] else 0)

        content.append(page_content)
    return content

def save_intermediate(content, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    pdf_path = r"G:\Ddrive\BatangD\task\workdiary\1. 매일정리\5. 공부및일지\공부\250208_NLPtext\2. Regular Expressions, Text Normalization, Edit Distance.pdf"
    base_name = os.path.basename(pdf_path).replace(".pdf", "")
    output_json = f"{base_name}_extracted.json"
    img_dir = "images"
    
    print(f"Extracting content (text, images, tables) from {pdf_path}...")
    data = extract_content(pdf_path, img_dir)
    save_intermediate(data, output_json)
    print(f"Extraction complete. Data saved to {output_json} and images to {img_dir}/")
