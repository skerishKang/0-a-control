import re
import os

def convert_transcript_to_html(input_file, output_file):
    """
    Converts a plain text transcript (optionally with timestamps) into 
    Coursera-style HTML transcript blocks.
    
    Expected format: 
    00:00 [Speaker] Text...
    OR 
    00:00 Text...
    """
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    html_blocks = []
    
    # Simple regex to catch [MM:SS] or MM:SS
    timestamp_re = re.compile(r'^(\d{1,2}:\d{2})\s*(.*)')

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        match = timestamp_re.match(line)
        if match:
            ts, text = match.groups()
        else:
            ts = "--:--"
            text = line
            
        block = f"""
        <div class="transcript-item">
            <span class="timestamp">{ts}</span>
            <span class="text-content">{text}</span>
        </div>"""
        html_blocks.append(block)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(html_blocks))

    print(f"Successfully converted to {output_file}")
    print("Copy-paste the contents into the <div id=\"transcript-container\"> section of your template.")

if __name__ == "__main__":
    # Example usage
    # Create a dummy input for demonstration if needed, or let user run it.
    input_path = "transcript.txt"
    output_path = "transcript_blocks.html"
    
    if not os.path.exists(input_path):
        with open(input_path, 'w', encoding='utf-8') as f:
            f.write("00:00 안녕하세요. 강의를 시작합니다.\n00:15 인공지능은 무엇일까요?\n00:45 코세라 스타일 템플릿입니다.")
            
    convert_transcript_to_html(input_path, output_path)
