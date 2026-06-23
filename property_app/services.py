from django.db import models as django_models
from sentence_transformers import SentenceTransformer
from pgvector.django import CosineDistance
from .models import Location

# Load model once when the module is imported (not on every request)
# This saves time because loading the model takes a few seconds
_model = None


def get_model():
    """Load and return the sentence transformer model (lazy loading)."""
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def get_query_embedding(text):
    """Convert a text query into a 384-dimension vector."""
    model = get_model()
    embedding = model.encode(text).tolist()
    return embedding


def semantic_location_search(query_text, limit=10):
    """
    Search locations using semantic similarity.
    Returns locations ordered by cosine distance to the query vector.
    Closer distance = more similar = better match.
    """
    # Skip search if query is empty
    if not query_text or not query_text.strip():
        return Location.objects.none()

    # Convert query text to vector
    query_embedding = get_query_embedding(query_text)

    # Find locations with embeddings, ordered by cosine similarity
    locations = Location.objects.filter(
        is_active=True,
        embedding__isnull=False
    ).annotate(
        similarity=CosineDistance('embedding', query_embedding)
    ).order_by('similarity')[:limit]

    return locations

def combined_location_search(query_text, limit=10):
    """
    Combine normal text search + semantic search for better results.
    Strategy:
     First try exact/partial text match (fast, precise)
     Then add semantic similar results (AI-powered, finds related locations)
     Merge both results, remove duplicates
    """
    if not query_text or not query_text.strip():
        return Location.objects.filter(is_active=True)

    # Normal text search — exact city/country name match
    text_results = Location.objects.filter(
        is_active=True
    ).filter(
        django_models.Q(name__icontains=query_text) |
        django_models.Q(city__icontains=query_text) |
        django_models.Q(country__icontains=query_text) |
        django_models.Q(state__icontains=query_text)
    )

    # Semantic search — AI finds related locations
    semantic_results = semantic_location_search(query_text, limit=limit)

    # Collect IDs from both searches
    text_ids = list(text_results.values_list('id', flat=True))
    semantic_ids = list(semantic_results.values_list('id', flat=True))

    # Merge IDs — text results first (more precise), then semantic
    combined_ids = text_ids.copy()
    for sid in semantic_ids:
        if sid not in combined_ids:
            combined_ids.append(sid)

    combined_ids = combined_ids[:limit]

    # Return locations in merged order
    locations = Location.objects.filter(id__in=combined_ids, is_active=True)
    return locations

