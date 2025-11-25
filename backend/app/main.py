from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import reactions, websocket

app = FastAPI(title="Audience Feedback API", version="1.0.0")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
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