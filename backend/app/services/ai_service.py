"""
AI Service for Enhanced Chatbot Responses
Uses Google Gemini API as the primary AI engine for construction advice.
Supports text chat, vision analysis, and structured data extraction.
"""

import os
import json
import base64
import httpx
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", "")
GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")


class AIService:
    """AI service powered by Google Gemini API for lean construction."""

    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.base_url = GEMINI_BASE_URL
        self.model = GEMINI_MODEL
        self._http_client = None

    @property
    def http_client(self):
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=60.0)
        return self._http_client

    def get_construction_system_prompt(self) -> str:
        """System prompt for construction-focused AI responses."""
        return """You are an expert AI assistant specializing in lean construction management and construction project optimization.
You have deep knowledge of:

1. Lean Construction Principles:
   - Last Planner System (LPS)
   - Value Stream Mapping
   - Pull Planning
   - Daily Huddles
   - 5S Methodology
   - Kanban in Construction
   - Gemba Walks

2. Construction Waste Types (DOWNTIME):
   - Defects and rework
   - Overproduction
   - Waiting time
   - Non-utilized Talent
   - Transportation
   - Inventory
   - Motion
   - Extra Processing

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
If the user asks about topics outside construction, politely redirect them to construction-related assistance."""

    async def _call_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 1024,
    ) -> Optional[str]:
        """Call Gemini API with a text prompt."""
        if not self.api_key:
            return None

        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"

        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"{system_prompt}\n\n{prompt}"}]})
        else:
            contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_output_tokens,
                "topP": 0.9,
                "topK": 40,
            },
        }

        try:
            response = await self.http_client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()

            return None
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None

    async def _call_gemini_vision(
        self,
        prompt: str,
        image_data: bytes,
        mime_type: str = "image/jpeg",
        system_prompt: Optional[str] = None,
        temperature: float = 0.4,
    ) -> Optional[str]:
        """Call Gemini with a text prompt + image for vision analysis."""
        if not self.api_key:
            return None

        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"

        image_b64 = base64.b64encode(image_data).decode("utf-8")

        parts = [
            {"inlineData": {"mimeType": mime_type, "data": image_b64}},
            {"text": prompt},
        ]

        if system_prompt:
            parts.insert(0, {"text": system_prompt})

        payload = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 2048,
                "topP": 0.9,
                "topK": 40,
            },
        }

        try:
            response = await self.http_client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()

            return None
        except Exception as e:
            print(f"Gemini Vision API error: {e}")
            return None

    async def _call_gemini_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> Optional[Dict[str, Any]]:
        """Call Gemini and parse the response as JSON."""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        full_prompt += "\n\nRespond ONLY with valid JSON. No markdown, no code fences, no explanation."

        result = await self._call_gemini(
            prompt=full_prompt,
            temperature=temperature,
            max_output_tokens=4096,
        )

        if not result:
            return None

        # Strip any markdown code fences
        result = result.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[-1] if "\n" in result else result[3:]
        if result.endswith("```"):
            result = result[:-3].strip()

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            print(f"Failed to parse Gemini structured response as JSON: {result[:200]}")
            return None

    # ============================================================
    # Text Chat
    # ============================================================

    async def generate_response(
        self, user_message: str, conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate AI response using Gemini. Falls back to rule-based if unavailable."""
        result = await self._call_gemini(
            prompt=user_message,
            system_prompt=self.get_construction_system_prompt(),
            temperature=0.7,
            max_output_tokens=1024,
        )
        if result:
            return result
        return self.get_rule_based_response(user_message)

    # ============================================================
    # Vision Analysis
    # ============================================================

    async def analyze_site_progress(
        self, image_data: bytes, mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """Analyze a construction site photo for progress tracking."""
        prompt = """Analyze this construction site image for progress monitoring.
Identify:
1. Current construction stage (foundation, framing, rough-in, drywall, interior finish, exterior, landscaping, etc.)
2. Estimated completion percentage
3. Visible activities and equipment
4. Any safety concerns or hazards visible
5. Overall site organization score (1-10)

Return your analysis as a JSON object with keys: stage, completion_percentage, activities, safety_concerns, site_organization_score, notes"""

        result = await self._call_gemini_vision(
            prompt=prompt,
            image_data=image_data,
            mime_type=mime_type,
            temperature=0.3,
        )

        if not result:
            return {
                "stage": "unknown",
                "completion_percentage": 0,
                "activities": [],
                "safety_concerns": [],
                "site_organization_score": 5,
                "notes": "Could not analyze image",
            }

        try:
            return json.loads(self._extract_json(result))
        except (json.JSONDecodeError, ValueError):
            return {"raw_analysis": result}

    async def analyze_safety(
        self, image_data: bytes, mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """Analyze a site photo for safety compliance."""
        prompt = """Analyze this construction site image for safety compliance.
Identify:
1. PPE compliance (helmets, vests, gloves, boots, harnesses)
2. Any safety violations or hazards visible
3. Housekeeping and site tidiness
4. Overall safety score (1-10)
5. Recommendations for improvement

Return your analysis as a JSON object with keys: ppe_compliance (list of items), violations (list), hazards (list), housekeeping_score, overall_safety_score, recommendations"""

        result = await self._call_gemini_vision(
            prompt=prompt,
            image_data=image_data,
            mime_type=mime_type,
            temperature=0.3,
        )

        if not result:
            return {
                "ppe_compliance": [],
                "violations": [],
                "hazards": [],
                "housekeeping_score": 5,
                "overall_safety_score": 5,
                "recommendations": ["Could not analyze image"],
            }

        try:
            return json.loads(self._extract_json(result))
        except (json.JSONDecodeError, ValueError):
            return {"raw_analysis": result}

    async def analyze_5s(
        self, image_data: bytes, mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """Analyze a site photo for 5S workplace organization."""
        prompt = """Analyze this construction site image for 5S workplace organization.
Score each S from 1-10:
1. Sort (Seiri) - Are unnecessary items removed?
2. Set in Order (Seiton) - Are tools and materials organized?
3. Shine (Seiso) - Is the workplace clean?
4. Standardize (Seiketsu) - Are standards visible?
5. Sustain (Shitsuke) - Is discipline maintained?

Return your analysis as a JSON object with keys: sort_score, set_in_order_score, shine_score, standardize_score, sustain_score, overall_score, observations, improvement_suggestions"""

        result = await self._call_gemini_vision(
            prompt=prompt,
            image_data=image_data,
            mime_type=mime_type,
            temperature=0.3,
        )

        if not result:
            return {
                "sort_score": 5,
                "set_in_order_score": 5,
                "shine_score": 5,
                "standardize_score": 5,
                "sustain_score": 5,
                "overall_score": 5,
                "observations": [],
                "improvement_suggestions": [],
            }

        try:
            return json.loads(self._extract_json(result))
        except (json.JSONDecodeError, ValueError):
            return {"raw_analysis": result}

    # ============================================================
    # Waste Detection
    # ============================================================

    async def detect_waste(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project data for DOWNTIME waste types using Gemini."""
        prompt = f"""Analyze this construction project data for lean waste detection.
Identify waste across all 8 DOWNTIME categories.

Project Data:
{json.dumps(project_data, indent=2)}

For each waste type detected, provide:
- detected: true/false
- severity_score: 1-10
- estimated_cost_impact: GBP
- estimated_time_impact: days
- root_causes: list of causes
- recommendations: list of actions

Return a JSON object with:
waste_analysis: object with keys for each waste type (defects, overproduction, waiting, non_utilized_talent, transportation, inventory, motion, extra_processing)
overall_waste_score: 1-100
total_estimated_waste_cost: GBP
priority_actions: list of top 5 priority recommendations"""

        result = await self._call_gemini_structured(
            prompt=prompt, system_prompt="You are a lean construction waste detection expert.", temperature=0.3
        )

        if not result:
            return {
                "waste_analysis": {},
                "overall_waste_score": 50,
                "total_estimated_waste_cost": 0,
                "priority_actions": ["Could not analyze project data"],
            }

        return result

    # ============================================================
    # Forecasting
    # ============================================================

    async def generate_forecast(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schedule and cost forecasts using Gemini."""
        prompt = f"""Analyze this construction project data and generate a detailed forecast.

Project Data:
{json.dumps(project_data, indent=2)}

Return a JSON forecast with:
schedule_forecast:
  predicted_completion_date: YYYY-MM-DD
  confidence_level: high/medium/low
  schedule_variance_days: number
  risk_factors: list of risks
  recommendations: list

cost_forecast:
  predicted_final_cost: GBP
  original_budget: GBP
  cost_variance_percentage: number
  risk_factors: list
  recommendations: list

overall_risk_assessment:
  risk_level: critical/high/medium/low
  key_concerns: list
  mitigation_strategies: list"""

        result = await self._call_gemini_structured(
            prompt=prompt,
            system_prompt="You are a construction project forecasting expert with 30 years of experience in cost and schedule prediction.",
            temperature=0.3,
        )

        if not result:
            return {
                "schedule_forecast": {"predicted_completion_date": "unknown", "confidence_level": "low"},
                "cost_forecast": {"predicted_final_cost": 0, "cost_variance_percentage": 0},
                "overall_risk_assessment": {"risk_level": "medium"},
            }

        return result

    # ============================================================
    # NLP Document Analysis
    # ============================================================

    async def analyze_document(self, document_text: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a construction document using Gemini NLP."""
        prompt = f"""Analyze this construction document.

Document Type: {document_type or "unknown"}
Document Content:
{document_text[:20000]}

Return a JSON analysis with:
document_type: classified type (RFI, submittal, change_order, safety_report, daily_log, meeting_minutes, contract, specification, other)
summary: 2-3 sentence summary
key_entities: list of people, organizations, locations, dates mentioned
risks_and_issues: list of identified risks
action_items: list of required actions
sentiment: positive/negative/neutral
priority: high/medium/low"""

        result = await self._call_gemini_structured(
            prompt=prompt,
            system_prompt="You are a construction document analysis expert specializing in contract review and risk assessment.",
            temperature=0.2,
        )

        if not result:
            return {
                "document_type": document_type or "unknown",
                "summary": "Could not analyze document",
                "key_entities": [],
                "risks_and_issues": [],
                "action_items": [],
            }

        return result

    # ============================================================
    # Report Generation
    # ============================================================

    async def generate_report(
        self, project_data: Dict[str, Any], report_type: str = "daily", output_format: str = "json"
    ) -> str:
        """Generate a construction project report using Gemini."""
        prompt = f"""Generate a {report_type} construction project report.

Project Data:
{json.dumps(project_data, indent=2)}

Report Requirements:
- Type: {report_type} (daily/weekly/monthly/executive/comprehensive)
- Cover key metrics, progress, waste analysis, and recommendations
- Be specific and data-driven

Provide the report in {output_format} format."""

        if output_format == "json":
            system = "You are a construction reporting expert. Return your report as valid JSON."
        else:
            system = "You are a construction reporting expert. Return a well-formatted report."

        result = await self._call_gemini(
            prompt=prompt,
            system_prompt=system,
            temperature=0.4,
            max_output_tokens=4096,
        )

        return result or "Report generation failed."

    # ============================================================
    # Lean Tools
    # ============================================================

    async def analyze_value_stream(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a value stream using Gemini."""
        prompt = f"""Analyze this construction process data for value stream mapping.

Process Data:
{json.dumps(process_data, indent=2)}

Return a JSON analysis with:
current_state:
  total_lead_time_days: number
  total_value_added_time_days: number
  total_non_value_added_time_days: number
  process_efficiency_percentage: number
  bottlenecks: list
  wastes_identified: list

improvement_opportunities: list of recommendations with expected impact
future_state_projection: brief description of optimized process"""

        result = await self._call_gemini_structured(
            prompt=prompt,
            system_prompt="You are a lean construction value stream mapping expert.",
            temperature=0.3,
        )

        return result or {
            "current_state": {"process_efficiency_percentage": 50, "wastes_identified": []},
            "improvement_opportunities": [],
        }

    # ============================================================
    # Rule-Based Fallback
    # ============================================================

    def get_rule_based_response(self, user_message: str) -> str:
        """Fallback rule-based responses when Gemini is unavailable."""
        import random

        message_lower = user_message.lower()

        responses = {
            "schedule|timeline": [
                "For scheduling, I recommend using the Last Planner System (LPS) to improve reliability and reduce waste.",
                "Consider implementing the Critical Path Method (CPM) with pull planning for better schedule reliability.",
                "Daily huddles and look-ahead planning are essential for schedule management.",
            ],
            "cost|budget": [
                "Cost management requires careful tracking. Consider earned value management (EVM) for better cost control.",
                "Value engineering can optimize costs without compromising quality.",
                "Implement proper change order management to control cost variations.",
            ],
            "quality|defect": [
                "Quality management focuses on preventing defects rather than inspecting them out.",
                "Use poka-yoke (mistake-proofing) techniques to prevent quality issues at the source.",
            ],
            "safety": [
                "Safety is paramount. Implement regular toolbox talks and near-miss reporting.",
                "Use Job Hazard Analysis (JHA) for high-risk activities.",
            ],
            "waste|lean": [
                "Lean construction identifies 8 wastes (DOWNTIME). Focus on eliminating these through value stream mapping.",
                "Implement 5S methodology (Sort, Set, Shine, Standardize, Sustain) to reduce waste.",
            ],
        }

        for keywords, replies in responses.items():
            if any(kw in message_lower for kw in keywords.split("|")):
                return random.choice(replies)

        return random.choice([
            "I'd be happy to help optimize your construction processes. What specific area interests you?",
            "That's a great question about lean construction. Let me assist you with evidence-based approaches.",
            "I can help with project management, scheduling, quality control, and construction efficiency.",
            "For construction efficiency, consider pull planning, daily huddles, and standardized work.",
        ])

    def _extract_json(self, text: str) -> str:
        """Extract JSON from text that may contain markdown or other content."""
        text = text.strip()
        # Remove markdown code fences
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first line (```json or ```)
            if len(lines) > 1:
                text = "\n".join(lines[1:])
            # Remove last line if it's ```
            if text.endswith("```"):
                text = text[:-3].strip()
        # Find JSON object boundaries
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return text[start : end + 1]
        return text

    async def close(self):
        """Close the HTTP client."""
        if self._http_client:
            await self._http_client.aclose()


# Global AI service instance
ai_service = AIService()
