from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.routers import reactions, websocket

# Load environment variables
load_dotenv()

app = FastAPI(title="Audience Feedback API", version="1.0.0")

# CORS middleware
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reactions.router)
app.include_router(websocket.router)

@app.get("/")
async def root():
    return {"message": "Audience Feedback API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}