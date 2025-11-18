import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any

app = FastAPI(title="Webino Solutions API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InquiryIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    company: Optional[str] = Field(None, max_length=150)
    service: Optional[str] = Field(None, description="Requested service category")
    message: str = Field(..., min_length=10, max_length=2000)
    budget: Optional[str] = Field(None)
    timeline: Optional[str] = Field(None)


@app.get("/")
def read_root():
    return {"message": "Webino Solutions API is running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from Webino Solutions backend!"}


@app.get("/api/services")
def get_services() -> List[Dict[str, Any]]:
    return [
        {
            "id": "web-dev",
            "title": "Web Design & Development",
            "description": "Modern, fast, and accessible websites built on React, Next.js, and Tailwind.",
        },
        {
            "id": "ecommerce",
            "title": "E-commerce Solutions",
            "description": "Conversion-focused online stores with secure payments and inventory tools.",
        },
        {
            "id": "branding",
            "title": "Branding & UI/UX",
            "description": "Cohesive brand systems and delightful interfaces that users love.",
        },
        {
            "id": "seo",
            "title": "SEO & Performance",
            "description": "Technical SEO, Core Web Vitals, and ongoing optimization for growth.",
        },
    ]


@app.post("/api/inquiries")
def create_inquiry(payload: InquiryIn):
    # Persist to MongoDB using provided helpers
    try:
        from database import create_document
        collection_name = "inquiry"  # from schemas: Inquiry -> inquiry
        inserted_id = create_document(collection_name, payload)
        return {"status": "success", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
