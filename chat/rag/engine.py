"""
RAG engine for Algerian law.

Uses LlamaIndex + Chroma for retrieval.
Generation is currently stubbed (returns top contexts + citation list).
"""
from pathlib import Path
from typing import Dict, Any, List

from django.conf import settings

from llama_index.core import StorageContext, load_index_from_storage
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb


def get_index(collection_name: str = "algerian_law"):
    """Load persisted Chroma index."""
    persist_dir = Path(settings.BASE_DIR) / "data" / "processed" / "chroma"

    if not (persist_dir / "chroma.sqlite3").exists() and not list(persist_dir.glob("*")):
        raise RuntimeError(
            "No vector index found. Run: python manage.py ingest_laws --codes civil"
        )

    chroma_client = chromadb.PersistentClient(path=str(persist_dir))
    chroma_collection = chroma_client.get_or_create_collection(name=collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store, persist_dir=str(persist_dir)
    )

    index = load_index_from_storage(storage_context)
    return index


def retrieve(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Return top relevant passages with metadata."""
    try:
        index = get_index()
    except Exception as e:
        return [{"error": str(e)}]

    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = retriever.retrieve(query)

    results = []
    for node in nodes:
        meta = node.node.metadata or {}
        results.append({
            "text": node.node.get_content()[:1500],
            "score": float(node.score) if node.score else 0.0,
            "code": meta.get("code", "Unknown"),
            "article": meta.get("article", ""),
            "source_file": meta.get("source_file", ""),
        })
    return results


def answer_query(query: str, lang: str = "fr", top_k: int = 5) -> Dict[str, Any]:
    """
    RAG generation using OpenRouter (OpenAI compatible API).
    """
    contexts = retrieve(query, top_k=top_k)

    if contexts and "error" in contexts[0]:
        return {
            "answer": f"Index not ready: {contexts[0]['error']}",
            "citations": [],
            "context_used": [],
            "lang": lang,
        }

    if not contexts:
        return {
            "answer": "Aucune information pertinente trouvée dans les textes actuellement indexés.",
            "citations": [],
            "context_used": [],
            "lang": lang,
        }

    citations = []
    context_texts = []
    for c in contexts[:3]:
        context_texts.append(f"Source: {c['code']} - {c['article']}\nTexte: {c['text'][:800]}")
        citations.append({
            "code": c["code"],
            "article": c["article"],
            "source_file": c["source_file"],
            "score": round(c["score"], 3),
        })

    prompt_context = "\n\n".join(context_texts)
    
    system_prompt = (
        f"You are a helpful legal assistant specializing in Algerian law. "
        f"You must answer the user's question in {lang} based ONLY on the provided context. "
        f"Always cite the relevant article and code in your answer. "
        f"If the context does not contain enough information to answer, state clearly that you cannot answer based on the provided texts."
    )
    user_prompt = f"Context texts:\n{prompt_context}\n\nQuestion: {query}"

    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
        response = client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        answer = response.choices[0].message.content
    except Exception as e:
        # Fallback if API fails
        answer = f"Error calling OpenRouter LLM: {str(e)}\n\nFallback context:\n" + "\n".join([f"- {c['article']} ({c['code']})" for c in citations])

    return {
        "answer": answer,
        "citations": citations,
        "context_used": [c["text"][:300] for c in contexts[:3]],
        "lang": lang,
    }

