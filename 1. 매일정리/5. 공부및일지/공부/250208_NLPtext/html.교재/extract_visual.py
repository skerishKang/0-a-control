import fitz
import os
import json

def extract_visual_elements(pdf_path, output_img_dir):
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

        # 1. Identify "visual" areas (drawings/images)
        drawings = page.get_drawings()
        visual_rects = []
        for d in drawings:
            visual_rects.append(d["rect"])
        
        # Merge overlapping rects for snapshots
        merged_rects = []
        for r in visual_rects:
            if not merged_rects:
                merged_rects.append(r)
            else:
                merged_last = merged_rects[-1]
                if r.intersects(merged_last):
                    merged_rects[-1] = merged_last | r
                else:
                    merged_rects.append(r)
        
        # Capture snapshots of merged visual areas
        for i, rect in enumerate(merged_rects):
            # Only if it's significant size
            if rect.width > 20 and rect.height > 20:
                pix = page.get_pixmap(clip=rect, matrix=fitz.Matrix(2, 2)) # Zoom for better quality
                img_filename = f"page{page_num+1}_vis{i+1}.png"
                pix.save(os.path.join(output_img_dir, img_filename))
                page_content["elements"].append({
                    "type": "image",
                    "src": f"images/{img_filename}",
                    "bbox": list(rect)
                })

        # 2. Extract Text Blocks (skip those inside visual areas if they are part of a diagram)
        blocks = page.get_text("blocks")
        for b in blocks:
            rect = fitz.Rect(b[:4])
            is_in_visual = False
            for vr in merged_rects:
                if rect.intersects(vr) and vr.width > rect.width * 1.5:
                    is_in_visual = True
                    break
            
            if not is_in_visual:
                text = b[4].strip()
                if text:
                    page_content["elements"].append({
                        "type": "text",
                        "content": text,
                        "bbox": b[:4]
                    })

        # Sort elements by y-position
        page_content["elements"].sort(key=lambda x: x["bbox"][1] if x["bbox"] else 0)
        content.append(page_content)
        
    return content

if __name__ == "__main__":
    pdf_path = r"G:\Ddrive\BatangD\task\workdiary\1. 매일정리\5. 공부및일지\공부\250208_NLPtext\2. Regular Expressions, Text Normalization, Edit Distance.pdf"
    img_dir = "images"
    print(f"Extracting visual elements from {pdf_path}...")
    data = extract_visual_elements(pdf_path, img_dir)
    with open("visual_extracted.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Extraction complete.")
