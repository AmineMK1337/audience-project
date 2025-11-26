from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
from datetime import datetime

from app.schemas.reacts import save_reaction
from app.schemas.questions import save_question, get_recent_questions

from app.agents.pacing_agent import pacing_agent
from app.agents.grouper_agent import grouper_agent, get_grouped_questions

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.presenter_connections: List[WebSocket] = []
        self.audience_connections: List[WebSocket] = []
        
        self.reaction_counts = {
            "speed_up": 0,
            "slow_down": 0,
            "im_lost": 0,
            "show_code": 0
        }
        
        # Add question counter for grouper agent
        self.question_count = 0

    async def connect_presenter(self, websocket: WebSocket):
        await websocket.accept()
        self.presenter_connections.append(websocket)

    async def connect_audience(self, websocket: WebSocket):
        await websocket.accept()
        self.audience_connections.append(websocket)

    def disconnect_presenter(self, websocket: WebSocket):
        if websocket in self.presenter_connections:
            self.presenter_connections.remove(websocket)

    def disconnect_audience(self, websocket: WebSocket):
        if websocket in self.audience_connections:
            self.audience_connections.remove(websocket)

    async def broadcast_to_presenters(self, message: dict):
        for connection in self.presenter_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                # If sending fails, assume dead connection and ignore 
                # (clean up happens on disconnect event)
                pass
    
    def update_stats(self, reaction_type: str):
        if reaction_type in self.reaction_counts:
            self.reaction_counts[reaction_type] += 1

manager = ConnectionManager()

@router.websocket("/ws/presenter")
async def presenter_websocket(websocket: WebSocket):
    await manager.connect_presenter(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle Heartbeat (Critical for Mobile Presenters)
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                continue

            # 2. Handle Stats Request
            if message.get("type") == "get_stats":
                await websocket.send_text(json.dumps({
                    "type": "stats_update",
                    "counts": manager.reaction_counts,
                    "audience": len(manager.audience_connections)
                }))

    except WebSocketDisconnect:
        manager.disconnect_presenter(websocket)

@router.websocket("/ws/audience")
async def audience_websocket(websocket: WebSocket):
    await manager.connect_audience(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                continue 

            # Heartbeat for Mobile Audience 
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                continue

            if message.get("type") == "reaction":
                r_type = message.get("reaction")
            
                manager.update_stats(r_type)

                await manager.broadcast_to_presenters({
                    "type": "new_reaction",
                    "reaction": r_type,
                    "counts": manager.reaction_counts 
                })

            
                if r_type in ["im_lost", "slow_down"]:
                    try:
                        if hasattr(pacing_agent, 'generate'):
                            response = pacing_agent.generate(json.dumps(manager.reaction_counts))
                        elif hasattr(pacing_agent, 'run'):
                            response = pacing_agent.run(json.dumps(manager.reaction_counts))
                        elif hasattr(pacing_agent, 'chat'):
                            response = pacing_agent.chat(json.dumps(manager.reaction_counts))
                        else:
                            response = pacing_agent(json.dumps(manager.reaction_counts))
                        
                        # Parse the response
                        response_text = str(response)
                        cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
                        ai_response = json.loads(cleaned_text)
                        
                        if ai_response.get("status") in ["CRITICAL", "WARNING"]:
                            await manager.broadcast_to_presenters({
                                "type": "ai_alert",
                                "alert": ai_response
                            })
                    except Exception as e:
                        print(f"Pacing Agent failed: {e}")

                # save to db (to_thread to avoid lag)
                asyncio.create_task(
                    asyncio.to_thread(
                        save_reaction, 
                        name=message.get("name", "Anon"), 
                        reaction=r_type
                    )
                )

            elif message.get("type") == "question":
                q_text = message.get("question")
                
                manager.question_count += 1
                
                await manager.broadcast_to_presenters({
                    "type": "new_question",
                    "question": q_text,
                    "name": message.get("name", "Anon")
                })

                # Save to db (to_thread to avoid lag)
                asyncio.create_task(
                    asyncio.to_thread(
                        save_question, 
                        name=message.get("name", "Anon"), 
                        question=q_text
                    )
                )
                
                # Every 5 questions, trigger grouper agent
                if manager.question_count % 3 == 0:
                    asyncio.create_task(process_questions_batch())

    except WebSocketDisconnect:
        manager.disconnect_audience(websocket)

async def process_questions_batch():
    """Group recent questions using AI"""
    try:
        recent_questions = get_recent_questions(limit=20)
        
        if len(recent_questions) >= 3: 
            # Extract just question text for the grouper
            question_texts = [q['question'] for q in recent_questions]
            
            grouped = await asyncio.to_thread(get_grouped_questions, question_texts)
            
            if grouped:
                await manager.broadcast_to_presenters({
                    "type": "question_groups",
                    "groups": grouped
                })
                print(f"Grouped {len(recent_questions)} questions into themes")
        
    except Exception as e:
        print(f"Question grouping failed: {e}")

async def periodic_question_grouping():
    """Run question grouping every 3 minutes"""
    while True:
        await asyncio.sleep(180)  # 3 mins
        await process_questions_batch()

asyncio.create_task(periodic_question_grouping())