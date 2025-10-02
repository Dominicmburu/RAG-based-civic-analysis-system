from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
import numpy as np
from docx import Document
from docx.shared import Pt
import csv
import re

load_dotenv()

app = Flask(__name__)
CORS(app)

# Global variables for models and data
primary_model = None
secondary_model = None
index = None
df_chunks = None
llm_chain = None

def initialize_models():
    """Initialize all models and load data"""
    global primary_model, secondary_model, index, df_chunks, llm_chain
    
    # Load sentence transformer models
    primary_model = SentenceTransformer('all-mpnet-base-v2')
    secondary_model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')
    
    # Load FAISS index and metadata
    index = faiss.read_index("sdg_faiss.index")
    df_chunks = pd.read_csv("sdg_faiss_metadata.csv")
    
    # Initialize OpenAI LLM
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.3)
    
    # Create prompt template
    summary_prompt = PromptTemplate(
        input_variables=["context"],
        template="""
You are an expert policy analyst.
You are tasked with writing a professional, policy-oriented synthesis of a sustainable development challenge using UN language (but precise), based strictly on the following Extracted Information from multiple validated documents.

Extracted Information:
{context}

Objective:
Produce a coherent, evidence-rich analytical summary suitable for UN agencies, government stakeholders, and development partners. The summary must rely strictly on the provided Extracted Information and cite sources accordingly.

Requirements:

1. Structure & Flow:
- Begin with a **high-level framing paragraph** under the INTRODUCTION section, explaining why the issue is strategically important to national development, regional stability, or humanitarian priorities.
- Under MAIN BODY, structure your analysis using full paragraphs only — no bullet points or numbered sections.
- Ensure ideas flow logically with smooth transitions across sections.

2. Evidence Integration:
- For every factual claim, include a **footnote-style superscript citation marker**, e.g., [1], [2], etc.
- Integrate **numbers and disaggregated evidence** wherever possible — this is mandatory.
- Always prioritize the **most recent data**: 2025 > 2024 > 2023.
- Use **short document aliases** (e.g., *HER_PID.pdf*) in citations.

3. Language Style:
- Maintain a professional, analytical tone aligned with UN and CCA drafting standards.
- Avoid vague generalizations and empty phrasing.
- Use varied sentence structures and transitions for smooth readability.

4. Section Guidelines:

**TITLE**  
- Rephrase the original challenge into a concise, evidence-based analytical title (max 15 words) aligned with SDG themes.

**EXECUTIVE SUMMARY** (150-200 words)
- Concise overview of the challenge, key findings, and implications

**INTRODUCTION**  
- Define the development challenge and briefly explain its strategic relevance.

**MAIN BODY (auto-generated headings)**  
- Use thematic section headings based on the Extracted Information.
- Analyze causes, consequences, structural barriers, systemic linkages, and opportunities for response.

**CONCLUSION**  
- Provide a concise synthesis of insights based only on the Extracted Information.

**REFERENCES**  
- Format citations as footnotes using [1], [2], etc.

Target length: ~1000 words (~2 pages).
"""
    )
    
    llm_chain = LLMChain(llm=llm, prompt=summary_prompt)

def semantic_search(query, k=10):
    """Perform semantic search using ensemble of two models"""
    query_embedding_primary = primary_model.encode([query], normalize_embeddings=True)
    distances_primary, indices_primary = index.search(query_embedding_primary, k)

    query_embedding_enhanced = secondary_model.encode([query], normalize_embeddings=True)
    distances_enhanced, indices_enhanced = index.search(query_embedding_enhanced, k)

    combined_results = {}
    
    for score, idx in zip(distances_primary[0], indices_primary[0]):
        if idx != -1 and idx < len(df_chunks):
            chunk_id = df_chunks.iloc[idx]["chunk_id"]
            combined_results[chunk_id] = {
                "theme": df_chunks.iloc[idx]["theme"],
                "file": df_chunks.iloc[idx]["file_name"],
                "chunk_text": df_chunks.iloc[idx]["chunk_text"],
                "score_primary": float(score),
                "score_enhanced": 0.0,
                "idx": int(idx)
            }
    
    for score, idx in zip(distances_enhanced[0], indices_enhanced[0]):
        if idx != -1 and idx < len(df_chunks):
            chunk_id = df_chunks.iloc[idx]["chunk_id"]
            if chunk_id in combined_results:
                combined_results[chunk_id]["score_enhanced"] = float(score)
            else:
                combined_results[chunk_id] = {
                    "theme": df_chunks.iloc[idx]["theme"],
                    "file": df_chunks.iloc[idx]["file_name"],
                    "chunk_text": df_chunks.iloc[idx]["chunk_text"],
                    "score_primary": 0.0,
                    "score_enhanced": float(score),
                    "idx": int(idx)
                }

    for result in combined_results.values():
        result["combined_score"] = (result["score_primary"] * 0.7 + result["score_enhanced"] * 0.3)

    sorted_results = sorted(combined_results.values(), key=lambda x: x["combined_score"], reverse=True)
    return sorted_results[:k]

def extract_candidate_indicators(text):
    """Extract indicator candidates from text"""
    pattern = r'\b([\w\s]+(?:rate|ratio|index|level|score|coverage|prevalence|incidence))\b'
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    return list(set([m.strip().title() for m in matches]))

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "RAG Civic API is running"})

@app.route('/search', methods=['POST'])
def search():
    """Semantic search endpoint"""
    data = request.json
    query = data.get('query', '')
    k = data.get('k', 10)
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    results = semantic_search(query, k=k)
    return jsonify({"results": results})

@app.route('/generate_summary', methods=['POST'])
def generate_summary():
    """Generate challenge summary endpoint"""
    data = request.json
    challenge = data.get('challenge', '')
    k = data.get('k', 30)
    
    if not challenge:
        return jsonify({"error": "Challenge is required"}), 400
    
    results = semantic_search(challenge, k=k)
    
    docs_with_refs = []
    for res in results:
        text = res['chunk_text'].strip().replace('\n', ' ')
        source = res['file']
        docs_with_refs.append(f"{text} (Source: {source})")
    
    context_text = "\n\n".join(docs_with_refs)
    
    final_summary = llm_chain.run({"context": context_text})
    
    return jsonify({
        "challenge": challenge,
        "summary": final_summary,
        "sources_count": len(results)
    })

@app.route('/generate_indicators', methods=['POST'])
def generate_indicators():
    """Generate indicator matrix endpoint"""
    data = request.json
    challenge = data.get('challenge', '')
    k = data.get('k', 20)
    top_k = data.get('top_k', 5)
    
    if not challenge:
        return jsonify({"error": "Challenge is required"}), 400
    
    results = semantic_search(challenge, k=k)
    context_text = " ".join([res['chunk_text'] for res in results])
    candidates = extract_candidate_indicators(context_text)
    
    if not candidates:
        candidates = [f"{challenge} Indicator {i+1}" for i in range(top_k)]
    
    top_indicators = candidates[:top_k]
    
    indicators = []
    for ind in top_indicators:
        indicators.append({
            "indicator": ind,
            "purpose": f"This indicator measures progress on {challenge.lower()} and reflects impact on target populations.",
            "data_sources": "WHO / National Statistical Office / World Bank",
            "measurement_frequency": "Annual",
            "relevance_to_sdg": "SDG Target TBD"
        })
    
    return jsonify({
        "challenge": challenge,
        "indicators": indicators
    })

@app.route('/batch_process', methods=['POST'])
def batch_process():
    """Process multiple challenges in batch"""
    data = request.json
    challenges = data.get('challenges', [])
    k = data.get('k', 30)
    
    if not challenges:
        return jsonify({"error": "Challenges list is required"}), 400
    
    results = []
    for challenge in challenges:
        try:
            search_results = semantic_search(challenge, k=k)
            docs_with_refs = []
            for res in search_results:
                text = res['chunk_text'].strip().replace('\n', ' ')
                source = res['file']
                docs_with_refs.append(f"{text} (Source: {source})")
            
            context_text = "\n\n".join(docs_with_refs)
            summary = llm_chain.run({"context": context_text})
            
            context_text_indicators = " ".join([res['chunk_text'] for res in search_results])
            candidates = extract_candidate_indicators(context_text_indicators)
            if not candidates:
                candidates = [f"{challenge} Indicator {i+1}" for i in range(5)]
            
            indicators = []
            for ind in candidates[:5]:
                indicators.append({
                    "indicator": ind,
                    "purpose": f"This indicator measures progress on {challenge.lower()} and reflects impact on target populations.",
                    "data_sources": "WHO / National Statistical Office / World Bank",
                    "measurement_frequency": "Annual",
                    "relevance_to_sdg": "SDG Target TBD"
                })
            
            results.append({
                "challenge": challenge,
                "summary": summary,
                "indicators": indicators,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "challenge": challenge,
                "status": "error",
                "error": str(e)
            })
    
    return jsonify({"results": results})

if __name__ == '__main__':
    print("Initializing models...")
    initialize_models()
    print("Models loaded successfully!")
    print("Starting server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)