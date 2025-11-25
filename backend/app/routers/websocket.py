from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
from datetime import datetime

from app.schemas.reacts import save_reaction, ReactionType
from app.schemas.questions import save_question  # Add this import

router = APIRouter()

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        # Store presenter connections (dashboard viewers)
        self.presenter_connections: List[WebSocket] = []
        # Store audience connections 
        self.audience_connections: List[WebSocket] = []
    
    async def connect_presenter(self, websocket: WebSocket):
        """Connect presenter dashboard"""
        await websocket.accept()
        self.presenter_connections.append(websocket)
        print(f"Presenter connected. Total: {len(self.presenter_connections)}")
    
    async def connect_audience(self, websocket: WebSocket):
        """Connect audience member"""
        await websocket.accept()
        self.audience_connections.append(websocket)
        print(f"Audience member connected. Total: {len(self.audience_connections)}")
    
    def disconnect_presenter(self, websocket: WebSocket):
        """Disconnect presenter"""
        if websocket in self.presenter_connections:
            self.presenter_connections.remove(websocket)
            print(f"Presenter disconnected. Remaining: {len(self.presenter_connections)}")
    
    def disconnect_audience(self, websocket: WebSocket):
        """Disconnect audience member"""
        if websocket in self.audience_connections:
            self.audience_connections.remove(websocket)
            print(f"Audience disconnected. Remaining: {len(self.audience_connections)}")
    
    async def broadcast_to_presenters(self, message: dict):
        """Send message to all presenter dashboards"""
        if not self.presenter_connections:
            print("No presenters connected to broadcast to")
            return
            
        disconnected = []
        for connection in self.presenter_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                print(f"Error broadcasting to presenter: {e}")
                disconnected.append(connection)
        
        # Remove dead connections
        for connection in disconnected:
            self.disconnect_presenter(connection)
    
    async def send_to_audience_member(self, websocket: WebSocket, message: dict):
        """Send message to specific audience member"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Error sending to audience member: {e}")
            self.disconnect_audience(websocket)

# Global connection manager
manager = ConnectionManager()

@router.websocket("/ws/presenter")
async def presenter_websocket(websocket: WebSocket):
    """WebSocket endpoint for presenter dashboard"""
    await manager.connect_presenter(websocket)
    try:
        while True:
            # Keep connection alive and listen for presenter commands
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle presenter requests (like requesting latest data)
            if message.get("type") == "get_stats":
                # You can add real-time stats here
                await websocket.send_text(json.dumps({
                    "type": "stats_update",
                    "presenter_count": len(manager.presenter_connections),
                    "audience_count": len(manager.audience_connections),
                    "timestamp": datetime.now().isoformat()
                }))
                
    except WebSocketDisconnect:
        print("Presenter disconnected normally")
        manager.disconnect_presenter(websocket)
    except Exception as e:
        print(f"Error in presenter websocket: {e}")
        manager.disconnect_presenter(websocket)

@router.websocket("/ws/audience")
async def audience_websocket(websocket: WebSocket):
    """WebSocket endpoint for audience members"""
    try:
        await manager.connect_audience(websocket)
        
        while True:
            # Receive messages from audience (reactions, questions)
            data = await websocket.receive_text()
            print(f"Received from audience: {data}")
            
            try:
                message = json.loads(data)
            except json.JSONDecodeError as e:
                print(f"Invalid JSON received: {e}")
                await manager.send_to_audience_member(websocket, {
                    "type": "error",
                    "message": "Invalid JSON format"
                })
                continue
            
            if message.get("type") == "reaction":
                try:
                    # Save reaction to database
                    reaction_id = save_reaction(
                        name=message.get("name", "Anonymous"),
                        reaction=message.get("reaction")
                    )
                    print(f"Saved reaction with ID: {reaction_id}")
                    
                    # Broadcast reaction to all presenters
                    await manager.broadcast_to_presenters({
                        "type": "new_reaction",
                        "id": reaction_id,
                        "name": message.get("name", "Anonymous"),
                        "reaction": message.get("reaction"),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Confirm to the audience member
                    await manager.send_to_audience_member(websocket, {
                        "type": "reaction_confirmed",
                        "id": reaction_id
                    })
                    
                except Exception as e:
                    print(f"Error saving reaction: {e}")
                    await manager.send_to_audience_member(websocket, {
                        "type": "error",
                        "message": f"Failed to save reaction: {str(e)}"
                    })
            
            elif message.get("type") == "question":
                try:
                    # Save question to database
                    question_id = save_question(
                        name=message.get("name", "Anonymous"),
                        question=message.get("question")
                    )
                    print(f"Saved question with ID: {question_id}")
                    
                    # Broadcast question to all presenters
                    await manager.broadcast_to_presenters({
                        "type": "new_question",
                        "id": question_id,
                        "name": message.get("name", "Anonymous"),
                        "question": message.get("question"),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Confirm to audience member
                    await manager.send_to_audience_member(websocket, {
                        "type": "question_confirmed",
                        "id": question_id
                    })
                    
                except Exception as e:
                    print(f"Error handling question: {e}")
                    await manager.send_to_audience_member(websocket, {
                        "type": "error",
                        "message": f"Failed to save question: {str(e)}"
                    })
            else:
                await manager.send_to_audience_member(websocket, {
                    "type": "error",
                    "message": "Unknown message type"
                })
                
    except WebSocketDisconnect:
        print("Audience member disconnected normally")
        manager.disconnect_audience(websocket)
    except Exception as e:
        print(f"Error in audience websocket: {e}")
        manager.disconnect_audience(websocket)

# Utility function to broadcast system messages
async def broadcast_system_message(message: dict):
    """Broadcast system-wide messages"""
    await manager.broadcast_to_presenters(message)