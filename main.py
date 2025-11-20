import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import AthProduct

app = FastAPI(title="Athleisure Brand API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Athleisure Backend Running"}

@app.get("/api/products", response_model=List[AthProduct])
def list_products(
    gender: Optional[str] = Query(None, description="men, women, unisex"),
    category: Optional[str] = Query(None, description="leggings, joggers, tops, sports-bra, hoodies, shorts"),
    q: Optional[str] = Query(None, description="search query across title, description, tags"),
    limit: int = Query(50, ge=1, le=100)
):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    filter_dict = {}
    if gender:
        filter_dict["gender"] = gender
    if category:
        filter_dict["category"] = category
    if q:
        # Simple text search across fields
        filter_dict["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"tags": {"$elemMatch": {"$regex": q, "$options": "i"}}},
        ]

    docs = get_documents("athproduct", filter_dict, limit)
    # Normalize image fields and ensure required keys
    normalized = []
    for d in docs:
        d.pop("_id", None)
        normalized.append(AthProduct(**d))
    return normalized

class ProductCreate(AthProduct):
    pass

@app.post("/api/products", status_code=201)
def create_product(product: ProductCreate):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    inserted_id = create_document("athproduct", product)
    return {"id": inserted_id}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except ImportError:
        response["database"] = "❌ Database module not found"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
