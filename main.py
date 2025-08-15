"""
FastAPI backend for Real Estate Investment Analysis app
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv, find_dotenv
import time
import json
from typing import Dict

# Load environment variables from .env file
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
    print(f"🔍 Debug: .env file found at: {dotenv_path}")

# Import Firebase utilities
from backend.utils.firebase import initialize_firebase

# Initialize Firebase
initialize_firebase()

# Import routes
from backend.routes import property_router, user_router
# Import the property_analysis_router when ready to use it
# from backend.routes.property_analysis import router as property_analysis_router

# Create FastAPI app
app = FastAPI(
    title="DSCR Property Analyzer API",
    description="API for real estate investment property analysis",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(property_router, prefix="/api", tags=["property"])
app.include_router(user_router, prefix="/api", tags=["users"])
# Include the property_analysis_router when ready to use it
# app.include_router(property_analysis_router, prefix="/api", tags=["analysis"])

@app.get("/", tags=["health"])
async def health_check() -> Dict:
    """Health check endpoint."""
    return {"status": "ok", "timestamp": time.time()}

# Run the app
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting your DSCR Property Analyzer API...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🌐 API Health Check: http://localhost:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
