ntti"""
Chat API endpoints for managing conversations and messages.
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Body, WebSocket, WebSocketDisconnect
from fastapi import WebSocket
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
import uuid
import json

from ..auth import get_current_active_user, SECRET_KEY, ALGORITHM
from ..database import get_db
from ..models import User, ChatConversation, ChatMessage
from ..services.ai_service import ai_service

# Create router
router = APIRouter(prefix="/chat", tags=["chat"])

# Pydantic models for request/response
class ConversationResponse(BaseModel):
    session_id: str
    user_id: int
    created_at: datetime
    updated_at: datetime

class MessageResponse(BaseModel):
    id: int
    conversation_id: str
    content: str
    role: str
    timestamp: datetime

class MessageCreate(BaseModel):
    session_id: Optional[str] = None
    content: str = Field(..., min_length=1, max_length=1000)
    role: str = Field(default="user", pattern="^(user|assistant)$")

class MessageCreateResponse(BaseModel):
    user_message: MessageResponse
    bot_message: MessageResponse

class ConversationCreate(BaseModel):
    pass

class ConversationCreateResponse(BaseModel):
    session_id: str
    user_id: int
    created_at: datetime

# Simple bot responses for initial implementation
SIMPLE_RESPONSES = [
    "I understand you're asking about construction management. How can I help you today?",
    "That's a great question about lean construction practices. Let me assist you with that.",
    "I can help you with project management, scheduling, and construction workflows.",
    "Based on lean construction principles, I recommend focusing on value stream mapping.",
    "For construction efficiency, consider implementing pull planning and daily huddles.",
    "I'd be happy to help optimize your construction processes. What specific area interests you?",
]

def get_simple_response(user_message: str) -> str:
    """Generate a simple response based on user input."""
    import random
    
    # Simple keyword-based responses
    message_lower = user_message.lower()
    
    if "schedule" in message_lower or "timeline" in message_lower:
        return "For scheduling in construction, I recommend using the Last Planner System (LPS) to improve reliability and reduce waste."
    elif "cost" in message_lower or "budget" in message_lower:
        return "Cost management in construction requires careful tracking of direct and indirect costs. Consider implementing earned value management."
    elif "quality" in message_lower or "defect" in message_lower:
        return "Quality management in lean construction focuses on preventing defects rather than inspecting them out. Use design for manufacturability and constructability."
    elif "safety" in message_lower:
        return "Safety is paramount in construction. Implement regular toolbox talks and near-miss reporting to create a proactive safety culture."
    elif "waste" in message_lower:
        return "Lean construction identifies 7 types of waste: transportation, inventory, motion, waiting, overproduction, over-processing, and defects. Focus on eliminating these."
    elif "efficiency" in message_lower or "lean" in message_lower:
        return "Lean construction aims to maximize value and minimize waste. Key tools include value stream mapping, pull planning, and continuous improvement."
    else:
        return random.choice(SIMPLE_RESPONSES)

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for the authenticated user."""
    try:
        conversations = db.query(ChatConversation).filter(
            ChatConversation.user_id == current_user.id
        ).order_by(ChatConversation.updated_at.desc()).all()
        
        return [
            ConversationResponse(
                session_id=conv.session_id,
                user_id=conv.user_id,
                created_at=conv.created_at,
                updated_at=conv.updated_at
            )
            for conv in conversations
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversations: {str(e)}"
        )

@router.get("/conversations/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all messages for a specific conversation."""
    try:
        # Verify conversation belongs to authenticated user
        conversation = db.query(ChatConversation).filter(
            ChatConversation.session_id == session_id,
            ChatConversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get messages for the conversation
        messages = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation.id  # Use actual conversation ID
        ).order_by(ChatMessage.timestamp.asc()).all()
        
        return [
            MessageResponse(
                id=msg.id,
                conversation_id=conversation.session_id,  # Return session_id for frontend
                content=msg.content,
                role=msg.role,
                timestamp=msg.timestamp
            )
            for msg in messages
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving messages: {str(e)}"
        )

@router.post("/messages", response_model=MessageCreateResponse)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a new message and generate bot response."""
    try:
        session_id = message_data.session_id
        
        # If no session_id provided, create a new conversation
        if not session_id:
            session_id = str(uuid.uuid4())
            conversation = ChatConversation(
                session_id=session_id,
                user_id=current_user.id
            )
            db.add(conversation)
            db.commit()
        else:
            # Verify conversation exists and belongs to user
            conversation = db.query(ChatConversation).filter(
                ChatConversation.session_id == session_id,
                ChatConversation.user_id == current_user.id
            ).first()
            
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        
        # Save user message
        user_message = ChatMessage(
            conversation_id=conversation.id,  # Use actual conversation ID, not session_id
            content=message_data.content,
            role="user"
        )
        db.add(user_message)
        
        # Get conversation history for context
        conversation_history = []
        if session_id:
            previous_messages = db.query(ChatMessage).filter(
                ChatMessage.conversation_id == conversation.id
            ).order_by(ChatMessage.timestamp.asc()).all()
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in previous_messages[-10:]  # Last 10 messages for context
            ]
        
        # Generate AI-enhanced bot response
        try:
            bot_response_content = await ai_service.generate_response(
                message_data.content,
                conversation_history
            )
        except Exception as e:
            print(f"AI service error: {e}")
            bot_response_content = get_simple_response(message_data.content)
        
        bot_message = ChatMessage(
            conversation_id=conversation.id,  # Use actual conversation ID, not session_id
            content=bot_response_content,
            role="assistant"
        )
        db.add(bot_message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user_message)
        db.refresh(bot_message)
        
        return MessageCreateResponse(
            user_message=MessageResponse(
                id=user_message.id,
                conversation_id=conversation.session_id,  # Return session_id for frontend
                content=user_message.content,
                role=user_message.role,
                timestamp=user_message.timestamp
            ),
            bot_message=MessageResponse(
                id=bot_message.id,
                conversation_id=conversation.session_id,  # Return session_id for frontend
                content=bot_message.content,
                role=bot_message.role,
                timestamp=bot_message.timestamp
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending message: {str(e)}"
        )

@router.post("/conversations", response_model=ConversationCreateResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation."""
    try:
        session_id = str(uuid.uuid4())
        conversation = ChatConversation(
            session_id=session_id,
            user_id=current_user.id
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        return ConversationCreateResponse(
            session_id=conversation.session_id,
            user_id=conversation.user_id,
            created_at=conversation.created_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating conversation: {str(e)}"
        )

# WebSocket support for real-time messaging
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[int, str] = {}  # user_id -> session_id mapping

    async def connect(self, websocket: WebSocket, session_id: str, user_id: int):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.user_connections[user_id] = session_id

    def disconnect(self, session_id: str, user_id: int):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if user_id in self.user_connections:
            del self.user_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.user_connections:
            session_id = self.user_connections[user_id]
            if session_id in self.active_connections:
                await self.active_connections[session_id].send_text(message)

    async def broadcast_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, token: str):
    """WebSocket endpoint for real-time chat messaging."""
    try:
        # Verify token (simplified - in production use proper JWT verification)
        from ..auth import verify_token
        user = verify_token(token)
        if not user:
            await websocket.close(code=4401)
            return
        
        # Connect user
        await manager.connect(websocket, session_id, user.id)
        
        # Send welcome message
        await manager.send_personal_message(
            json.dumps({
                "type": "connected",
                "message": "Connected to chat",
                "session_id": session_id
            }), user.id
        )
        
        # Listen for messages
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "message":
                # Send typing indicator
                await manager.send_personal_message(
                    json.dumps({
                        "type": "typing",
                        "user_id": user.id,
                        "is_typing": True
                    }), user.id
                )
                
                # Process message (reuse existing logic)
                # This would integrate with the existing send_message logic
                
                # Send response
                await manager.send_personal_message(
                    json.dumps({
                        "type": "message",
                        "content": "Bot response received",
                        "timestamp": datetime.utcnow().isoformat()
                    }), user.id
                )
                
    except WebSocketDisconnect:
        manager.disconnect(session_id, user.id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(session_id, user.id)

# Enhanced endpoints with pagination and search
class ConversationSearch(BaseModel):
    query: str = Field(..., min_length=1, max_length=100)
    limit: int = Field(default=10, ge=1, le=50)
    offset: int = Field(default=0, ge=0)

@router.post("/conversations/search")
async def search_conversations(
    search_data: ConversationSearch,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search conversations by content or keywords."""
    try:
        # Search in conversation messages for the query
        messages = db.query(ChatMessage).join(ChatConversation).filter(
            ChatConversation.user_id == current_user.id,
            ChatMessage.content.ilike(f"%{search_data.query}%")
        ).order_by(ChatMessage.timestamp.desc()).offset(search_data.offset).limit(search_data.limit).all()
        
        # Group by conversation
        conversation_sessions = {}
        for msg in messages:
            conv_id = msg.conversation_id
            if conv_id not in conversation_sessions:
                conversation_sessions[conv_id] = {
                    "session_id": msg.conversation.session_id,
                    "last_message": msg.content,
                    "last_timestamp": msg.timestamp,
                    "message_count": 0
                }
            conversation_sessions[conv_id]["message_count"] += 1
        
        return {
            "conversations": list(conversation_sessions.values()),
            "total_found": len(conversation_sessions),
            "query": search_data.query
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )