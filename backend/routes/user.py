from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
import firebase_admin
from firebase_admin import firestore

from ..models.search import SearchRequest

router = APIRouter()

# Get Firestore client
try:
    db = firestore.client()
except Exception as e:
    print(f"⚠️ Firestore client initialization failed: {e}")
    db = None

@router.post("/save-search")
async def save_search(request: SearchRequest):
    """Save a search to user's profile"""
    if not db:
        raise HTTPException(status_code=503, detail="Firebase not available")
        
    try:
        search_data = {
            "city": request.city,
            "state": request.state,
            "down_payment": request.down_payment,
            "interest_rate": request.interest_rate,
            "min_price": request.min_price,
            "max_price": request.max_price,
            "created_at": datetime.now()
        }
        
        db.collection("users").document(request.username).collection("saved_searches").add(search_data)
        
        return {"message": "Search saved successfully!"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save search: {str(e)}")

@router.get("/saved-searches/{username}")
async def get_saved_searches(username: str):
    """Get all saved searches for a user"""
    if not db:
        raise HTTPException(status_code=503, detail="Firebase not available")
        
    try:
        saved_searches_ref = db.collection("users").document(username).collection("saved_searches")
        searches = []
        
        for s in saved_searches_ref.stream():
            data = s.to_dict()
            data["id"] = s.id
            searches.append(data)
        
        return searches
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch searches: {str(e)}")

@router.post("/test-firebase")
async def test_firebase():
    """Test Firebase connection"""
    if not db:
        raise HTTPException(status_code=503, detail="Firebase not available")
        
    try:
        doc_ref = db.collection("test").add({
            "message": "Hello from FastAPI!",
            "timestamp": datetime.now()
        })
        return {"message": "Successfully wrote to Firebase!", "doc_id": doc_ref[1].id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firebase test failed: {str(e)}")