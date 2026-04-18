import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

COLLECTION = "menu_items"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output dimension

_client = None
_model = None


def get_client():
    global _client
    if _client is None:
        url = os.getenv("QDRANT_URL", "http://localhost:6333")
        _client = QdrantClient(url=url)
    return _client


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def ensure_collection():
    client = get_client()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


def index_menu_items(restaurant_id):
    """
    Index all menu items for a restaurant into Qdrant.
    Called once when menu is first imported.
    """
    from restaurants.models import Category

    ensure_collection()
    client = get_client()
    model = get_model()

    categories = Category.objects.filter(
        restaurant_id=restaurant_id
    ).prefetch_related("menuitem_set")

    points = []
    for cat in categories:
        for item in cat.menuitem_set.all():
            text = f"{item.name} {cat.name} {item.description or ''} {item.ingredients or ''} {'veg' if item.menu_type == 'VEG' else 'non-veg'}"
            vector = model.encode(text).tolist()
            points.append(PointStruct(
                id=item.id,
                vector=vector,
                payload={
                    "restaurant_id": restaurant_id,
                    "category": cat.name,
                    "name": item.name,
                    "menu_type": item.menu_type,
                    "full_price": str(item.full_price),
                    "half_price": str(item.half_price) if item.half_price else None,
                    "description": item.description or "",
                    "ingredients": item.ingredients or "",
                    "available": item.available,
                },
            ))

    if points:
        client.upsert(collection_name=COLLECTION, points=points)


def upsert_menu_item(item):
    """
    Add or update a single menu item in Qdrant.
    Called when a new MenuItem is saved via signal.
    """
    ensure_collection()
    client = get_client()
    model = get_model()

    cat = item.category
    text = f"{item.name} {cat.name} {item.description or ''} {item.ingredients or ''} {'veg' if item.menu_type == 'VEG' else 'non-veg'}"
    vector = model.encode(text).tolist()
    
    client.upsert(
        collection_name=COLLECTION,
        points=[PointStruct(
            id=item.id,
            vector=vector,
            payload={
                "restaurant_id": cat.restaurant_id,
                "category": cat.name,
                "name": item.name,
                "menu_type": item.menu_type,
                "full_price": str(item.full_price),
                "half_price": str(item.half_price) if item.half_price else None,
                "description": item.description or "",
                "ingredients": item.ingredients or "",
                "available": item.available,
            },
        )]
    )


def search_menu(query, restaurant_id, top_k=6):
    """
    Semantic search — returns top_k relevant menu items for the query.
    Filtered by restaurant_id so results are always restaurant-specific.
    """
    ensure_collection()
    client = get_client()
    model = get_model()

    vector = model.encode(query).tolist()
    results = client.query_points(
        collection_name=COLLECTION,
        query=vector,
        limit=top_k,
        query_filter=Filter(
            must=[FieldCondition(key="restaurant_id", match=MatchValue(value=restaurant_id))]
        ),
    )
    return [hit.payload for hit in results.points]
