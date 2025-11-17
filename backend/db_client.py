from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

_client = None
_db = None

def get_db():
    global _client, _db

    if _client is None:
        _client = MongoClient(MONGO_URI)
        _db = _client[DB_NAME]

    return _db

def insert_review(collection, doc):
    db = get_db()
    return db[collection].insert_one(doc).inserted_id

def get_reviews(collection, q={}, limit=100):
    db = get_db()
    return list(db[collection].find(q).limit(limit))

def close_db():
    global _client
    if _client is not None:
        _client.close()
        _client = None
        print("MongoDB client closed.")

def clear_reviews_on_exit():
    """Clear the reviews collection and close the MongoDB client."""
    global _client, _db
    try:
        if _db:
            print("\n[INFO] Clearing 'reviews' collection before shutdown...")
            _db["reviews"].delete_many({})
            print("[INFO] All reviews deleted successfully.")
    except Exception as e:
        print(f"[WARN] Failed to clear reviews: {e}")
    finally:
        if _client:
            _client.close()
            print("[INFO] MongoDB client connection closed.")