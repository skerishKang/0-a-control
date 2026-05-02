from mcp.server.fastmcp import FastMCP
import traceback
from sentence_transformers import SentenceTransformer
import os
import fitz  # PyMuPDF
import faiss
import numpy as np

mcp = FastMCP("docReader")
model = SentenceTransformer("all-MiniLM-L6-v2")

def load_and_chunk_documents(folder):
    docs = []
    for filename in os.listdir(folder):
        if filename.endswith(".pdf"):
            doc = fitz.open(os.path.join(folder, filename))
            for page in doc:
                text = page.get_text()
                if text.strip():
                    docs.append(text)
    return docs

def build_or_load_index(chunks):
    embeddings = model.encode(chunks)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype(np.float32))
    return index, chunks

def search_similar_chunks(query, index, chunks, top_k=3):
    query_vec = model.encode([query])
    D, I = index.search(np.array(query_vec).astype(np.float32), top_k)
    return [chunks[i] for i in I[0]]

@mcp.tool()
def search_pdf(query: str):
    try:
        docs = load_and_chunk_documents("docs/")
        index, chunks = build_or_load_index(docs)
        results = search_similar_chunks(query, index, chunks)
        prompt_response = "\n".join([
            "다음 문단을 참고하여 질문에 답해주세요:\n",
            *[f"- {chunk}" for chunk in results],
            f"\n질문: {query}"
        ])
        return prompt_response
    except Exception as e:
        print("Tool 실행 중 오류 발생:", e)
        traceback.print_exc()
        return "오류 발생: 파일을 찾을 수 없습니다."

if __name__ == "__main__":
    mcp.run() 