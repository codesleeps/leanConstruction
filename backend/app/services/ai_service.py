# AI Service for Enhanced Chatbot Responses
# Supports OpenAI and Anthropic APIs for intelligent construction advice.

import os
import asyncio
from typing import List, Dict, Any
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

class AIService:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
        
        # Initialize clients if API keys are available
        if self.openai_api_key and OPENAI_AVAILABLE:
            self.openai_client = AsyncOpenAI(api_key=self.openai_api_key)
        
        if self.anthropic_api_key and ANTHROPIC_AVAILABLE:
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=self.anthropic_api_key)
    
    def get_construction_system_prompt(self) -> str:
        """Get the system prompt for construction-focused AI responses."""
        return """
You are an expert AI assistant specializing in lean construction management and construction project optimization. 
You have deep knowledge of:

1. Lean Construction Principles:
   - Last Planner System (LPS)
   - Value Stream Mapping
   - Pull Planning
   - Daily Huddles
   - 5S Methodology
   - Kanban in Construction
   - Gemba Walks

2. Construction Waste Types:
   - Defects and rework
   - Waiting time
   - Transportation
   - Overprocessing
   - Overproduction
   - Inventory
   - Motion

3. Construction Management:
   - Project scheduling and critical path method
   - Cost management and earned value analysis
   - Quality control and assurance
   - Safety management systems
   - Risk assessment and mitigation
   - Stakeholder communication
   - Change order management

4. Technology Integration:
   - BIM (Building Information Modeling)
   - IoT sensors for construction sites
   - AI/ML for predictive analytics
   - Computer vision for quality control
   - Mobile apps for field communication

5. Industry Best Practices:
   - Design for constructability
   - Modular and prefabricated construction
   - Sustainable construction practices
   - Workforce training and development
   - Equipment utilization optimization

Provide practical, actionable advice tailored to the user's specific construction challenges.
Keep responses concise but informative. When appropriate, suggest specific tools, methodologies, or next steps.
If the user asks about topics outside construction, politely redirect them to construction-related assistance.
"""
    
    async def generate_openai_response(self, user_message: str, conversation_history: list = None) -> str:
        """Generate response using OpenAI API."""
        if not self.openai_client:
            return None
            
        try:
            messages = [
                {"role": "system", "content": self.get_construction_system_prompt()}
            ]
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history[-10:]:  # Keep last 10 messages
                    messages.append({"role": msg["role"], "content": msg["content"]})
            
            messages.append({"role": "user", "content": user_message})
            
            response = await self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None
    
    async def generate_anthropic_response(self, user_message: str, conversation_history: list = None) -> str:
        """Generate response using Anthropic Claude API."""
        if not self.anthropic_client:
            return None
            
        try:
            # Build conversation context
            context = self.get_construction_system_prompt()
            context += f"\n\nHuman: {user_message}\n\nAssistant:"
            
            if conversation_history:
                # Add conversation history as context
                history_text = "\n\n".join([
                    f"Human: {msg['content']}" if msg['role'] == 'user' else f"Assistant: {msg['content']}"
                    for msg in conversation_history[-10:]  # Keep last 10 messages
                ])
                context = f"{self.get_construction_system_prompt()}\n\nPrevious conversation:\n{history_text}\n\nHuman: {user_message}\n\nAssistant:"
            
            response = await self.anthropic_client.messages.create(
                model=self.anthropic_model,
                max_tokens=500,
                messages=[{"role": "user", "content": context}],
                temperature=0.7,
                top_p=0.9,
                top_k=50,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            print(f"Anthropic API error: {e}")
            return None
    
    async def generate_response(self, user_message: str, conversation_history: list = None) -> str:
        """
        Generate AI response using the best available service.
        Prefers OpenAI, falls back to Anthropic, then to rule-based responses.
        """
        # Try OpenAI first
        if self.openai_client:
            response = await self.generate_openai_response(user_message, conversation_history)
            if response:
                return response
        
        # Try Anthropic as fallback
        if self.anthropic_client:
            response = await self.generate_anthropic_response(user_message, conversation_history)
            if response:
                return response
        
        # Fallback to rule-based responses
        return self.get_rule_based_response(user_message)
    
    def get_rule_based_response(self, user_message: str) -> str:
        """Enhanced rule-based responses for construction topics."""
        import random
        
        message_lower = user_message.lower()
        
        # Construction-specific responses
        if "schedule" in message_lower or "timeline" in message_lower:
            responses = [
                "For scheduling in construction, I recommend using the Last Planner System (LPS) to improve reliability and involves reduce waste. This collaborative scheduling with trade partners and daily commitment planning.",
                "Consider implementing the Critical Path Method (CPM) for complex projects. Combined with pull planning, this can significantly improve schedule reliability.",
                "Daily huddles and look-ahead planning are essential for schedule management. Focus on making work ready before starting it."
            ]
        elif "cost" in message_lower or "budget" in message_lower:
            responses = [
                "Cost management in construction requires careful tracking of direct and indirect costs. Consider implementing earned value management (EVM) for better cost control.",
                "Value engineering can help optimize costs without compromising quality. Focus on eliminating non-value-adding activities.",
                "Implement proper change order management processes to control cost variations and maintain budget integrity."
            ]
        elif "quality" in message_lower or "defect" in message_lower:
            responses = [
                "Quality management in lean construction focuses on preventing defects rather than inspecting them out. Use design for manufacturability and constructability.",
                "Implement Last Planner System to ensure work is planned to the right sequence, with the right people, and with the right flow.",
                "Consider using poka-yoke (mistake-proofing) techniques to prevent quality issues at the source."
            ]
        elif "safety" in message_lower:
            responses = [
                "Safety is paramount in construction. Implement regular toolbox talks and near-miss reporting to create a proactive safety culture.",
                "Use Job Hazard Analysis (JHA) for high-risk activities and ensure all workers understand the safety protocols.",
                "Consider implementing behavior-based safety programs and daily safety huddles."
            ]
        elif "waste" in message_lower or "lean" in message_lower:
            responses = [
                "Lean construction identifies 7 types of waste: transportation, inventory, motion, waiting, overproduction, over-processing, and defects. Focus on eliminating these through value stream mapping.",
                "Implement 5S methodology (Sort, Set in Order, Shine, Standardize, Sustain) to improve workplace organization and reduce waste.",
                "Use the Last Planner System to improve workflow reliability and reduce waiting waste."
            ]
        elif "efficiency" in message_lower or "productivity" in message_lower:
            responses = [
                "For construction efficiency, consider implementing pull planning and daily huddles. This improves coordination and reduces delays.",
                "Use visual management techniques like kanban boards and andon systems to improve communication and identify issues quickly.",
                "Implement standardized work processes and continuous improvement (Kaizen) to gradually increase efficiency."
            ]
        elif "bim" in message_lower or "technology" in message_lower:
            responses = [
                "Building Information Modeling (BIM) can significantly improve coordination and reduce conflicts. Use 4D scheduling to link 3D models with project schedules.",
                "Consider implementing IoT sensors for real-time monitoring of site conditions, equipment utilization, and worker safety.",
                "Mobile apps can improve field-to-office communication and enable real-time decision making."
            ]
        elif "planning" in message_lower or "last planner" in message_lower:
            responses = [
                "The Last Planner System involves 6 phases: Master Schedule, Phase Schedule, Pull Planning, Weekly Work Plans, Daily Huddles, and Learning Sessions.",
                "Focus on making work ready (6Ms: Man, Machine, Method, Material, Mother Nature, Milieu) before planning to execute it.",
                "Use percent plan complete (PPC) to measure schedule reliability and identify root causes of variance."
            ]
        else:
            responses = [
                "I understand you're asking about construction management. How can I help you optimize your construction processes today?",
                "That's a great question about lean construction practices. Let me assist you with evidence-based approaches.",
                "I can help you with project management, scheduling, quality control, and construction efficiency. What specific area interests you?",
                "Based on lean construction principles, I recommend focusing on value stream mapping and continuous improvement.",
                "For construction efficiency, consider implementing pull planning, daily huddles, and standardized work processes.",
                "I'd be happy to help optimize your construction workflows. What specific challenges are you facing?"
            ]
        
        return random.choice(responses)

# Global AI service instance
ai_service = AIService()