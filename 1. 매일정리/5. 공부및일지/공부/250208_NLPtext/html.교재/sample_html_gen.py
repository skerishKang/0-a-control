import json
import os

# Sample content from the first 3 pages (previously extracted manually/mentally for this demonstration)
# Jurafsky & Martin, Chapter 2
content = [
    {
        "page": 1,
        "title": "Chapter 2: Regular Expressions, Text Normalization, Edit Distance",
        "sections": [
            {
                "en": "The dialogue above is from ELIZA, an early natural language processing system that could carry on a limited conversation with a user by imitating the responses of a Rogerian psychotherapist.",
                "ko": "위의 대화는 로저스 학파 심리치료사의 응답을 모방하여 사용자와 제한적인 대화를 나눌 수 있었던 초기 자연어 처리 시스템인 ELIZA의 것입니다."
            },
            {
                "en": "ELIZA is a surprisingly simple program that uses pattern matching to recognize phrases like 'I need X' and translate them into matching responses like 'What would it mean to you if you got X'.",
                "ko": "ELIZA는 'I need X'와 같은 문구를 인식하기 위해 패턴 매칭을 사용하고, 이를 'What would it mean to you if you got X'와 같은 일치하는 응답으로 변환하는 놀라울 정도로 단순한 프로그램입니다."
            }
        ]
    },
    {
        "page": 2,
        "title": "2.1 Regular Expressions",
        "sections": [
            {
                "en": "One of the most important tools in text processing is the regular expression. A regular expression (RE) is a formula in a special language that is used for specifying search strings.",
                "ko": "텍스트 처리에서 가장 중요한 도구 중 하나는 정규 표현식입니다. 정규 표현식(RE)은 검색 문자열을 지정하는 데 사용되는 특수 언어의 공식입니다."
            },
            {
                "en": "Regular expressions are used for everything from simple search-and-replace to capturing the complex structures of natural language.",
                "ko": "정규 표현식은 단순한 찾기 및 바꾸기부터 자연어의 복잡한 구조를 캡처하는 것까지 모든 작업에 사용됩니다."
            }
        ]
    }
]

html_template = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Course Study Guide: NLP Chapter 2</title>
    <style>
        :root {{
            --primary: #1e293b;
            --secondary: #334155;
            --bg: #ffffff;
            --card-bg: #f8fafc;
            --text-en: #0f172a;
            --text-ko: #475569;
            --accent: #2563eb;
            --border: #e2e8f0;
        }}
        body {{
            font-family: 'Inter', system-ui, sans-serif;
            background-color: var(--bg);
            color: var(--text-en);
            margin: 0;
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            margin-bottom: 4rem;
            padding: 2.5rem;
            background: var(--card-bg);
            border-radius: 1rem;
            border: 1px solid var(--border);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
        h1 {{ margin: 0; font-size: 2.5rem; color: var(--primary); }}
        header p {{ color: var(--text-ko); font-size: 1.1rem; margin-top: 0.5rem; }}
        .page {{
            background: var(--bg);
            border-radius: 1rem;
            padding: 2.5rem;
            margin-bottom: 3rem;
            border: 1px solid var(--border);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.02);
        }}
        .section {{
            margin-bottom: 2.5rem;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border);
        }}
        .section:last-child {{ border-bottom: none; }}
        @media (max-width: 768px) {{
            .section {{ grid-template-columns: 1fr; gap: 1.5rem; }}
        }}
        .en {{ font-weight: 500; font-size: 1.15rem; color: var(--text-en); }}
        .ko {{ color: var(--text-ko); font-family: 'Noto Sans KR', sans-serif; font-size: 1.1rem; }}
        .badge {{
            display: inline-block;
            padding: 0.35rem 1rem;
            background: var(--accent);
            color: #ffffff;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Natural Language Processing</h1>
            <p>Chapter 2: Regular Expressions, Text Normalization, Edit Distance</p>
        </header>

        {content_html}
    </div>
</body>
</html>
"""

def generate_html(json_data, output_file):
    with open(json_data, 'r', encoding='utf-8') as f:
        data = json.load(f)

    content_html = ""
    for page in data: # Process all pages
        content_html += f'<div class="page"><div class="badge">Page {page["page"]}</div>'
        for el in page["elements"]:
            if el["type"] == "text":
                en_text = el["content"].replace('\n', ' ')
                ko_text = el.get("ko", "")
                
                content_html += f'''
                <div class="section">
                    <div class="en">{en_text}</div>
                    <div class="ko">{ko_text if ko_text else ""}</div>
                </div>
                '''
            elif el["type"] == "image":
                content_html += f'''
                <div class="visual">
                    <img src="{el["src"]}" alt="Figure from PDF">
                    <p class="caption">Figure {el["src"].split("_")[1].replace(".png", "")} extracted from PDF</p>
                </div>
                '''
        content_html += '</div>'

    # Add custom styles for visuals
    full_html = html_template.replace('</style>', """
        .visual {{
            text-align: center;
            margin: 2rem 0;
            padding: 1rem;
            background: #fff;
            border: 1px solid var(--border);
            border-radius: 0.5rem;
        }}
        .visual img {{
            max-width: 100%;
            height: auto;
            border-radius: 0.25rem;
        }}
        .caption {{
            font-size: 0.9rem;
            color: var(--text-ko);
            margin-top: 0.5rem;
            font-style: italic;
        }}
    </style>""").format(content_html=content_html)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    generate_html("translated_visual.json", "study_guide_visual.html")
    print("Study guide with visuals and full translations generated: study_guide_visual.html")
