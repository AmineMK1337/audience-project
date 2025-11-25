from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

from app.schemas.reacts import save_reaction, get_recent_reactions, ReactionType

router = APIRouter(prefix="/api", tags=["reactions"])

class ReactionRequest(BaseModel):
    name: str
    reaction: ReactionType

@router.post("/reactions")
async def submit_reaction(request: ReactionRequest):
    """Submit audience reaction"""
    try:
        reaction_id = save_reaction(request.name, request.reaction)
        return {"success": True, "id": reaction_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reactions/recent")
async def get_reactions(limit: int = 50):
    """Get recent reactions for presenter dashboard"""
    try:
        reactions = get_recent_reactions(limit)
        return {"reactions": reactions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))