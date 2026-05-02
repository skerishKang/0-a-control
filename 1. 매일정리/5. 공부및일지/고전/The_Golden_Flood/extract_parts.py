#!/usr/bin/env python3
import re
import html

def clean_text(text):
    # HTML entities 디코딩
    text = html.unescape(text)
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 여러 개의 공백을 하나로 변환
    text = re.sub(r'\s+', ' ', text)
    
    # 문장 부호 주변 정리
    text = re.sub(r'\s+([.!?,:;])', r'\1', text)
    text = re.sub(r'([.!?])\s*([A-Z])', r'\1\n\n\2', text)
    
    # 대화 부분 정리 (따옴표로 시작하는 부분)
    text = re.sub(r'"\s*([^"]+)\s*"', r'"\1"', text)
    
    return text.strip()

def extract_part(content, start_line, end_line=None):
    lines = content.split('\n')
    
    if end_line:
        part_lines = lines[start_line-1:end_line-1]
    else:
        part_lines = lines[start_line-1:]
    
    part_content = '\n'.join(part_lines)
    return clean_text(part_content)

# HTML 파일 읽기
html_file = r"G:\Ddrive\BatangD\task\workdiary\5. 공부및일지\고전\The_Golden_Flood\golden_flood.html"

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("HTML 파일 읽기 완료")

# Part별 추출
# Part 1: 라인 134-1695 (Part Two 시작 전까지)
part1 = extract_part(content, 134, 1695)

# Part 2: 라인 1696-2651 (Part Three 시작 전까지) 
part2 = extract_part(content, 1696, 2651)

# Part 3: 라인 2652부터 끝까지 (END OF GUTENBERG 제외)
lines = content.split('\n')
part3_lines = []
start_found = False

for i, line in enumerate(lines[2651:], 2652):
    if 'END OF THE PROJECT GUTENBERG EBOOK' in line:
        break
    if 'PART III: THE PARADOXICAL PANIC' in line:
        start_found = True
        continue
    if start_found:
        part3_lines.append(line)

part3_content = '\n'.join(part3_lines)
part3 = clean_text(part3_content)

# 파일로 저장
parts = [
    ("Part One - The Flood", part1),
    ("Part Two - The Gold", part2), 
    ("Part Three - The Paradoxical Panic", part3)
]

for title, text in parts:
    filename = title.lower().replace(' ', '_').replace('-', '_') + '.txt'
    filepath = f"G:\\Ddrive\\BatangD\\task\\workdiary\\5. 공부및일지\\고전\\The_Golden_Flood\\{filename}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"THE GOLDEN FLOOD\n{title.upper()}\n{'='*60}\n\n")
        f.write(text)
    
    print(f"{title}: {len(text)} 문자 -> {filename}")
    print(f"미리보기: {text[:200]}...\n")

print("모든 Part 추출 완료!")