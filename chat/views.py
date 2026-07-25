"""
DRF views for lawdz Algerian law chatbot API.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

DISCLAIMER = (
    "This is for informational purposes only and is NOT legal advice. "
    "Always consult a qualified Algerian lawyer and official sources."
)

@api_view(["POST"])
def chat(request):
    """
    POST /api/chat/
    Body: { "query": "...", "lang": "fr" | "ar" (optional) }
    """
    query = request.data.get("query", "").strip()
    if not query:
        return Response({"error": "query is required"}, status=status.HTTP_400_BAD_REQUEST)

    from chat.rag.engine import answer_query

    lang = request.data.get("lang", "fr")
    
    # Call the RAG engine
    rag_response = answer_query(query, lang=lang)

    return Response({
        "query": query,
        "answer": rag_response["answer"],
        "citations": rag_response["citations"],
        "disclaimer": DISCLAIMER,
        "used_context_count": len(rag_response.get("context_used", [])),
    })


@api_view(["GET"])
def sources(request):
    """List available codes / ingested sources (stub)."""
    return Response({
        "codes": [
            {"name": "Code Civil", "version": "1975 + 2007 amendments"},
            {"name": "Code de la Famille", "version": "1984 + amendments"},
        ],
        "note": "Ingestion pipeline coming in Phase 1-2."
    })
