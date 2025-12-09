"""
NLP Models for Document and Communication Analysis - Phase 3

Implements BERT-based NLP for construction document analysis:
- Document Classification (RFIs, submittals, change orders, safety reports)
- Named Entity Recognition for construction terms
- Sentiment Analysis for communication tone
- Text Summarization for long documents
- Risk and Issue Extraction
- Contract Clause Analysis
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, Counter
import logging
import re
import json
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# Check for transformers availability
try:
    from transformers import (
        AutoTokenizer,
        AutoModelForSequenceClassification,
        AutoModelForTokenClassification,
        AutoModelForSeq2SeqLM,
        pipeline
    )
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available. Using rule-based fallbacks.")


# ============================================
# Enums and Data Classes
# ============================================

class DocumentType(Enum):
    """Types of construction documents"""
    RFI = "rfi"                          # Request for Information
    SUBMITTAL = "submittal"              # Submittal
    CHANGE_ORDER = "change_order"        # Change Order
    SAFETY_REPORT = "safety_report"      # Safety Report
    DAILY_LOG = "daily_log"              # Daily Log
    MEETING_MINUTES = "meeting_minutes"  # Meeting Minutes
    CONTRACT = "contract"                # Contract Document
    SPECIFICATION = "specification"      # Specification
    PUNCH_LIST = "punch_list"            # Punch List
    INSPECTION = "inspection"            # Inspection Report
    INCIDENT = "incident"                # Incident Report
    PROGRESS_REPORT = "progress_report"  # Progress Report
    CORRESPONDENCE = "correspondence"    # General Correspondence
    UNKNOWN = "unknown"


class EntityType(Enum):
    """Named entity types for construction domain"""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    MONEY = "money"
    MATERIAL = "material"
    EQUIPMENT = "equipment"
    TRADE = "trade"
    SPECIFICATION = "specification"
    ROOM = "room"
    FLOOR = "floor"
    BUILDING = "building"
    TASK = "task"
    ISSUE = "issue"
    RISK = "risk"


class SentimentLevel(Enum):
    """Sentiment levels"""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


class UrgencyLevel(Enum):
    """Urgency levels for communications"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


@dataclass
class DocumentClassification:
    """Result of document classification"""
    document_type: DocumentType
    confidence: float
    secondary_type: Optional[DocumentType] = None
    keywords: List[str] = field(default_factory=list)


@dataclass
class NamedEntity:
    """Named entity extracted from text"""
    text: str
    entity_type: EntityType
    start: int
    end: int
    confidence: float


@dataclass
class SentimentResult:
    """Sentiment analysis result"""
    sentiment: SentimentLevel
    score: float
    positive_indicators: List[str] = field(default_factory=list)
    negative_indicators: List[str] = field(default_factory=list)


@dataclass
class RiskItem:
    """Identified risk from document"""
    description: str
    category: str
    severity: str
    source_text: str
    confidence: float


@dataclass
class ActionItem:
    """Action item extracted from text"""
    description: str
    assignee: Optional[str]
    due_date: Optional[str]
    priority: str
    source_text: str


# ============================================
# Document Classifier
# ============================================

class DocumentClassifier:
    """
    BERT-based document classifier for construction documents
    
    Classifies documents into predefined categories:
    RFI, Submittal, Change Order, Safety Report, etc.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        
        # Keywords for rule-based classification fallback
        self.keyword_patterns = {
            DocumentType.RFI: [
                r'\brfi\b', r'request for information', r'clarification required',
                r'please clarify', r'information requested', r'question regarding'
            ],
            DocumentType.SUBMITTAL: [
                r'\bsubmittal\b', r'shop drawing', r'product data',
                r'sample submission', r'material submittal', r'review and approve'
            ],
            DocumentType.CHANGE_ORDER: [
                r'change order', r'\bco[\s\-]?\d+', r'modification',
                r'cost adjustment', r'scope change', r'contract modification'
            ],
            DocumentType.SAFETY_REPORT: [
                r'safety', r'incident', r'accident', r'injury',
                r'hazard', r'\bppe\b', r'osha', r'safety violation'
            ],
            DocumentType.DAILY_LOG: [
                r'daily log', r'daily report', r'field report',
                r'weather.*conditions', r'manpower', r'work performed'
            ],
            DocumentType.MEETING_MINUTES: [
                r'meeting minutes', r'attendees', r'agenda',
                r'action items', r'discussion', r'next meeting'
            ],
            DocumentType.CONTRACT: [
                r'\bcontract\b', r'agreement', r'terms and conditions',
                r'parties agree', r'obligations', r'indemnification'
            ],
            DocumentType.PUNCH_LIST: [
                r'punch list', r'punchlist', r'deficiency',
                r'incomplete item', r'correction required'
            ],
            DocumentType.INSPECTION: [
                r'inspection', r'inspector', r'passed', r'failed',
                r'code compliance', r'building official'
            ],
            DocumentType.INCIDENT: [
                r'incident report', r'near miss', r'emergency',
                r'first aid', r'medical attention'
            ],
            DocumentType.PROGRESS_REPORT: [
                r'progress report', r'percent complete', r'milestone',
                r'schedule status', r'completion date'
            ]
        }
        
        if model_path and TRANSFORMERS_AVAILABLE:
            self._load_model()
    
    def _load_model(self):
        """Load pre-trained model"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path or "bert-base-uncased"
            )
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_path or "bert-base-uncased",
                num_labels=len(DocumentType)
            )
            self.is_loaded = True
            logger.info("Document classifier model loaded")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.is_loaded = False
    
    def classify(self, text: str) -> DocumentClassification:
        """
        Classify a document based on its text content
        
        Args:
            text: Document text content
            
        Returns:
            DocumentClassification with type and confidence
        """
        if self.is_loaded and TRANSFORMERS_AVAILABLE:
            return self._classify_with_model(text)
        else:
            return self._classify_with_rules(text)
    
    def _classify_with_model(self, text: str) -> DocumentClassification:
        """Use BERT model for classification"""
        try:
            inputs = self.tokenizer(
                text[:512],  # Truncate to max length
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)
                
            top_idx = torch.argmax(probs).item()
            confidence = probs[0][top_idx].item()
            
            # Get second highest
            probs_sorted, indices = torch.sort(probs[0], descending=True)
            secondary_idx = indices[1].item()
            
            doc_type = list(DocumentType)[top_idx]
            secondary_type = list(DocumentType)[secondary_idx]
            
            # Extract keywords
            keywords = self._extract_keywords(text, doc_type)
            
            return DocumentClassification(
                document_type=doc_type,
                confidence=confidence,
                secondary_type=secondary_type if probs_sorted[1] > 0.15 else None,
                keywords=keywords
            )
        except Exception as e:
            logger.error(f"Model classification failed: {e}")
            return self._classify_with_rules(text)
    
    def _classify_with_rules(self, text: str) -> DocumentClassification:
        """Rule-based classification fallback"""
        text_lower = text.lower()
        scores = {}
        
        for doc_type, patterns in self.keyword_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                score += len(matches)
            scores[doc_type] = score
        
        # Sort by score
        sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_types[0][1] == 0:
            return DocumentClassification(
                document_type=DocumentType.UNKNOWN,
                confidence=0.3,
                keywords=[]
            )
        
        # Normalize confidence
        total_score = sum(s for _, s in sorted_types if s > 0)
        confidence = sorted_types[0][1] / total_score if total_score > 0 else 0.5
        
        # Get keywords that matched
        keywords = self._extract_keywords(text, sorted_types[0][0])
        
        return DocumentClassification(
            document_type=sorted_types[0][0],
            confidence=min(confidence, 0.95),
            secondary_type=sorted_types[1][0] if sorted_types[1][1] > 0 else None,
            keywords=keywords[:10]
        )
    
    def _extract_keywords(self, text: str, doc_type: DocumentType) -> List[str]:
        """Extract relevant keywords for the document type"""
        keywords = []
        text_lower = text.lower()
        
        patterns = self.keyword_patterns.get(doc_type, [])
        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            keywords.extend(matches)
        
        return list(set(keywords))[:10]


# ============================================
# Named Entity Recognition
# ============================================

class ConstructionNER:
    """
    Named Entity Recognition for construction domain
    
    Extracts construction-specific entities:
    - Materials, Equipment, Trades
    - Locations (rooms, floors, buildings)
    - Specifications, Tasks, Issues
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        
        # Construction domain vocabulary
        self.domain_vocab = {
            EntityType.MATERIAL: [
                'concrete', 'steel', 'rebar', 'lumber', 'drywall', 'insulation',
                'brick', 'block', 'glass', 'aluminum', 'copper', 'pvc', 'hvac',
                'ductwork', 'piping', 'conduit', 'wire', 'cable', 'roofing',
                'flooring', 'tile', 'carpet', 'paint', 'sealant', 'adhesive'
            ],
            EntityType.EQUIPMENT: [
                'crane', 'excavator', 'bulldozer', 'forklift', 'scaffold',
                'loader', 'backhoe', 'compressor', 'generator', 'pump',
                'mixer', 'saw', 'drill', 'welder', 'lift', 'truck'
            ],
            EntityType.TRADE: [
                'electrician', 'plumber', 'carpenter', 'mason', 'welder',
                'hvac technician', 'roofer', 'painter', 'ironworker',
                'glazier', 'drywall installer', 'flooring installer'
            ],
            EntityType.SPECIFICATION: [
                'spec', 'specification', 'astm', 'ansi', 'aci', 'aisc',
                'nfpa', 'ibc', 'nec', 'ul listed', 'fire rated'
            ]
        }
        
        # Regex patterns for specific entities
        self.patterns = {
            EntityType.DATE: r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',
            EntityType.MONEY: r'\$[\d,]+(?:\.\d{2})?|\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars?|usd)\b',
            EntityType.ROOM: r'room\s+[\w\-]+|rm\s*[\w\-]+',
            EntityType.FLOOR: r'floor\s+\d+|level\s+\d+|\d+(?:st|nd|rd|th)\s+floor',
            EntityType.BUILDING: r'building\s+[\w\-]+|bldg\s*[\w\-]+'
        }
        
        if model_path and TRANSFORMERS_AVAILABLE:
            self._load_model()
    
    def _load_model(self):
        """Load NER model"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path or "dslim/bert-base-NER"
            )
            self.model = AutoModelForTokenClassification.from_pretrained(
                self.model_path or "dslim/bert-base-NER"
            )
            self.is_loaded = True
            logger.info("NER model loaded")
        except Exception as e:
            logger.error(f"Failed to load NER model: {e}")
    
    def extract_entities(self, text: str) -> List[NamedEntity]:
        """
        Extract named entities from text
        
        Args:
            text: Input text
            
        Returns:
            List of NamedEntity objects
        """
        entities = []
        
        # Use model if available for general NER
        if self.is_loaded and TRANSFORMERS_AVAILABLE:
            general_entities = self._extract_with_model(text)
            entities.extend(general_entities)
        
        # Always apply domain-specific extraction
        domain_entities = self._extract_domain_entities(text)
        entities.extend(domain_entities)
        
        # Apply pattern-based extraction
        pattern_entities = self._extract_pattern_entities(text)
        entities.extend(pattern_entities)
        
        # Deduplicate
        entities = self._deduplicate_entities(entities)
        
        return entities
    
    def _extract_with_model(self, text: str) -> List[NamedEntity]:
        """Use BERT NER model"""
        entities = []
        try:
            ner_pipeline = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy="simple"
            )
            
            results = ner_pipeline(text[:1000])  # Limit text length
            
            entity_mapping = {
                'PER': EntityType.PERSON,
                'ORG': EntityType.ORGANIZATION,
                'LOC': EntityType.LOCATION,
                'MISC': EntityType.TASK
            }
            
            for result in results:
                entity_type = entity_mapping.get(
                    result['entity_group'],
                    EntityType.TASK
                )
                entities.append(NamedEntity(
                    text=result['word'],
                    entity_type=entity_type,
                    start=result['start'],
                    end=result['end'],
                    confidence=result['score']
                ))
        except Exception as e:
            logger.error(f"Model NER failed: {e}")
        
        return entities
    
    def _extract_domain_entities(self, text: str) -> List[NamedEntity]:
        """Extract construction domain entities"""
        entities = []
        text_lower = text.lower()
        
        for entity_type, vocab in self.domain_vocab.items():
            for term in vocab:
                pattern = r'\b' + re.escape(term) + r'\b'
                for match in re.finditer(pattern, text_lower):
                    entities.append(NamedEntity(
                        text=text[match.start():match.end()],
                        entity_type=entity_type,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.85
                    ))
        
        return entities
    
    def _extract_pattern_entities(self, text: str) -> List[NamedEntity]:
        """Extract entities using regex patterns"""
        entities = []
        
        for entity_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(NamedEntity(
                    text=match.group(),
                    entity_type=entity_type,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.90
                ))
        
        return entities
    
    def _deduplicate_entities(self, entities: List[NamedEntity]) -> List[NamedEntity]:
        """Remove duplicate entities"""
        seen = set()
        unique = []
        
        for entity in entities:
            key = (entity.text.lower(), entity.entity_type)
            if key not in seen:
                seen.add(key)
                unique.append(entity)
        
        return unique


# ============================================
# Sentiment Analyzer
# ============================================

class CommunicationAnalyzer:
    """
    Sentiment and tone analysis for construction communications
    
    Analyzes:
    - Email tone
    - Meeting sentiment
    - Issue urgency
    - Communication clarity
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        
        # Sentiment indicators
        self.positive_indicators = [
            'thank', 'appreciate', 'excellent', 'great', 'good job',
            'well done', 'pleased', 'satisfied', 'ahead of schedule',
            'under budget', 'successful', 'approved', 'resolved'
        ]
        
        self.negative_indicators = [
            'urgent', 'immediately', 'problem', 'issue', 'concern',
            'delay', 'behind schedule', 'over budget', 'failed',
            'rejected', 'deficient', 'unacceptable', 'disappointed',
            'frustrated', 'complaint', 'critical', 'asap'
        ]
        
        self.urgency_indicators = {
            UrgencyLevel.CRITICAL: [
                'emergency', 'critical', 'stop work', 'safety hazard',
                'immediately', 'life safety', 'urgent action required'
            ],
            UrgencyLevel.HIGH: [
                'urgent', 'asap', 'priority', 'time sensitive',
                'today', 'by end of day', 'critical path'
            ],
            UrgencyLevel.MEDIUM: [
                'soon', 'this week', 'follow up', 'please address',
                'attention needed', 'action required'
            ],
            UrgencyLevel.LOW: [
                'when possible', 'at your convenience', 'fyi',
                'for your information', 'no rush'
            ]
        }
        
        if model_path and TRANSFORMERS_AVAILABLE:
            self._load_model()
    
    def _load_model(self):
        """Load sentiment model"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path or "distilbert-base-uncased-finetuned-sst-2-english"
            )
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_path or "distilbert-base-uncased-finetuned-sst-2-english"
            )
            self.is_loaded = True
            logger.info("Sentiment model loaded")
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
    
    def analyze_sentiment(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of communication
        
        Args:
            text: Communication text
            
        Returns:
            SentimentResult with level and indicators
        """
        if self.is_loaded and TRANSFORMERS_AVAILABLE:
            return self._analyze_with_model(text)
        else:
            return self._analyze_with_rules(text)
    
    def _analyze_with_model(self, text: str) -> SentimentResult:
        """Use model for sentiment analysis"""
        try:
            sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer
            )
            
            result = sentiment_pipeline(text[:512])[0]
            
            # Map model output to sentiment levels
            label = result['label'].lower()
            score = result['score']
            
            if label == 'positive':
                if score > 0.9:
                    sentiment = SentimentLevel.VERY_POSITIVE
                else:
                    sentiment = SentimentLevel.POSITIVE
            else:
                if score > 0.9:
                    sentiment = SentimentLevel.VERY_NEGATIVE
                else:
                    sentiment = SentimentLevel.NEGATIVE
            
            # Get indicators
            pos_found, neg_found = self._find_indicators(text)
            
            return SentimentResult(
                sentiment=sentiment,
                score=score if label == 'positive' else -score,
                positive_indicators=pos_found,
                negative_indicators=neg_found
            )
        except Exception as e:
            logger.error(f"Model sentiment failed: {e}")
            return self._analyze_with_rules(text)
    
    def _analyze_with_rules(self, text: str) -> SentimentResult:
        """Rule-based sentiment analysis"""
        text_lower = text.lower()
        
        pos_found, neg_found = self._find_indicators(text)
        
        pos_count = len(pos_found)
        neg_count = len(neg_found)
        
        # Calculate sentiment score
        total = pos_count + neg_count
        if total == 0:
            return SentimentResult(
                sentiment=SentimentLevel.NEUTRAL,
                score=0.0,
                positive_indicators=pos_found,
                negative_indicators=neg_found
            )
        
        score = (pos_count - neg_count) / total
        
        # Map to sentiment level
        if score > 0.5:
            sentiment = SentimentLevel.VERY_POSITIVE
        elif score > 0.2:
            sentiment = SentimentLevel.POSITIVE
        elif score > -0.2:
            sentiment = SentimentLevel.NEUTRAL
        elif score > -0.5:
            sentiment = SentimentLevel.NEGATIVE
        else:
            sentiment = SentimentLevel.VERY_NEGATIVE
        
        return SentimentResult(
            sentiment=sentiment,
            score=score,
            positive_indicators=pos_found,
            negative_indicators=neg_found
        )
    
    def _find_indicators(self, text: str) -> Tuple[List[str], List[str]]:
        """Find positive and negative indicators"""
        text_lower = text.lower()
        
        pos_found = [ind for ind in self.positive_indicators if ind in text_lower]
        neg_found = [ind for ind in self.negative_indicators if ind in text_lower]
        
        return pos_found, neg_found
    
    def analyze_urgency(self, text: str) -> UrgencyLevel:
        """Determine urgency level of communication"""
        text_lower = text.lower()
        
        for level in [UrgencyLevel.CRITICAL, UrgencyLevel.HIGH,
                      UrgencyLevel.MEDIUM, UrgencyLevel.LOW]:
            indicators = self.urgency_indicators[level]
            for ind in indicators:
                if ind in text_lower:
                    return level
        
        return UrgencyLevel.INFORMATIONAL


# ============================================
# Text Summarizer
# ============================================

class DocumentSummarizer:
    """
    Summarizes construction documents
    
    Provides:
    - Extractive summarization
    - Key points extraction
    - Action items extraction
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        
        if model_path and TRANSFORMERS_AVAILABLE:
            self._load_model()
    
    def _load_model(self):
        """Load summarization model"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path or "facebook/bart-large-cnn"
            )
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_path or "facebook/bart-large-cnn"
            )
            self.is_loaded = True
            logger.info("Summarization model loaded")
        except Exception as e:
            logger.error(f"Failed to load summarization model: {e}")
    
    def summarize(
        self,
        text: str,
        max_length: int = 150,
        min_length: int = 50
    ) -> str:
        """
        Summarize document text
        
        Args:
            text: Document text
            max_length: Maximum summary length
            min_length: Minimum summary length
            
        Returns:
            Summary text
        """
        if self.is_loaded and TRANSFORMERS_AVAILABLE:
            return self._summarize_with_model(text, max_length, min_length)
        else:
            return self._summarize_extractive(text, max_length)
    
    def _summarize_with_model(
        self,
        text: str,
        max_length: int,
        min_length: int
    ) -> str:
        """Use model for summarization"""
        try:
            summarizer = pipeline(
                "summarization",
                model=self.model,
                tokenizer=self.tokenizer
            )
            
            # Handle long text by chunking
            if len(text) > 1024:
                chunks = self._chunk_text(text, 1024)
                summaries = []
                for chunk in chunks[:3]:  # Limit chunks
                    result = summarizer(
                        chunk,
                        max_length=max_length // len(chunks),
                        min_length=min_length // len(chunks),
                        do_sample=False
                    )
                    summaries.append(result[0]['summary_text'])
                return ' '.join(summaries)
            else:
                result = summarizer(
                    text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                return result[0]['summary_text']
        except Exception as e:
            logger.error(f"Model summarization failed: {e}")
            return self._summarize_extractive(text, max_length)
    
    def _summarize_extractive(self, text: str, max_length: int) -> str:
        """Extractive summarization fallback"""
        sentences = self._split_sentences(text)
        
        if not sentences:
            return text[:max_length]
        
        # Score sentences by importance
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = self._score_sentence(sentence, i, len(sentences))
            scored_sentences.append((sentence, score))
        
        # Sort by score and select top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Build summary
        summary_sentences = []
        current_length = 0
        
        for sentence, _ in scored_sentences:
            if current_length + len(sentence) <= max_length:
                summary_sentences.append(sentence)
                current_length += len(sentence)
        
        # Reorder by original position
        original_order = []
        for sentence in summary_sentences:
            idx = sentences.index(sentence)
            original_order.append((idx, sentence))
        
        original_order.sort(key=lambda x: x[0])
        
        return ' '.join(s for _, s in original_order)
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _score_sentence(
        self,
        sentence: str,
        position: int,
        total_sentences: int
    ) -> float:
        """Score sentence importance"""
        score = 0.0
        
        # Position scoring (first and last sentences often important)
        if position == 0:
            score += 2.0
        elif position < 3:
            score += 1.0
        elif position >= total_sentences - 2:
            score += 0.5
        
        # Length scoring (prefer medium-length sentences)
        words = len(sentence.split())
        if 10 <= words <= 25:
            score += 1.0
        elif words < 5:
            score -= 0.5
        
        # Keyword scoring
        important_keywords = [
            'important', 'critical', 'must', 'required', 'deadline',
            'issue', 'action', 'complete', 'approve', 'reject'
        ]
        for keyword in important_keywords:
            if keyword in sentence.lower():
                score += 0.5
        
        return score
    
    def _chunk_text(self, text: str, chunk_size: int) -> List[str]:
        """Split text into chunks"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) > chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def extract_key_points(self, text: str, max_points: int = 5) -> List[str]:
        """Extract key points from document"""
        sentences = self._split_sentences(text)
        
        key_patterns = [
            r'(?:must|shall|will|should)\s+\w+',
            r'(?:action required|please|ensure|verify)',
            r'(?:deadline|due date|by\s+\d)',
            r'(?:issue|problem|concern|risk)',
            r'(?:approve|reject|accept|deny)'
        ]
        
        key_sentences = []
        for sentence in sentences:
            for pattern in key_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    key_sentences.append(sentence)
                    break
        
        return key_sentences[:max_points]


# ============================================
# Risk and Issue Extractor
# ============================================

class RiskIssueExtractor:
    """
    Extracts risks and issues from construction documents
    
    Identifies:
    - Safety risks
    - Schedule risks
    - Cost risks
    - Quality issues
    - Compliance issues
    """
    
    def __init__(self):
        self.risk_patterns = {
            'safety': [
                r'safety\s+(?:hazard|concern|risk|issue)',
                r'(?:injury|accident|incident)\s+(?:risk|potential)',
                r'(?:fall|fire|electrical)\s+hazard',
                r'osha\s+violation'
            ],
            'schedule': [
                r'(?:delay|behind|slipping)\s+(?:schedule|deadline)',
                r'(?:schedule|timeline)\s+(?:risk|concern)',
                r'(?:critical\s+path|float)\s+(?:impact|affected)',
                r'(?:late|delayed)\s+(?:delivery|completion)'
            ],
            'cost': [
                r'(?:budget|cost)\s+(?:overrun|increase|risk)',
                r'(?:change\s+order|additional\s+cost)',
                r'(?:unforeseen|unexpected)\s+(?:expense|cost)',
                r'price\s+(?:increase|escalation)'
            ],
            'quality': [
                r'(?:quality|workmanship)\s+(?:issue|concern|defect)',
                r'(?:defective|deficient|substandard)',
                r'(?:rework|repair)\s+(?:required|needed)',
                r'(?:fails|does\s+not\s+meet)\s+(?:spec|standard)'
            ],
            'compliance': [
                r'(?:code|regulation)\s+(?:violation|non-compliance)',
                r'(?:permit|inspection)\s+(?:issue|failure)',
                r'(?:not\s+in)\s+compliance',
                r'(?:violation|citation)\s+(?:issued|received)'
            ]
        }
        
        self.severity_indicators = {
            'critical': ['critical', 'severe', 'major', 'significant', 'serious'],
            'high': ['high', 'important', 'substantial', 'considerable'],
            'medium': ['moderate', 'medium', 'potential', 'possible'],
            'low': ['minor', 'low', 'small', 'minimal']
        }
    
    def extract_risks(self, text: str) -> List[RiskItem]:
        """
        Extract risks from document text
        
        Args:
            text: Document text
            
        Returns:
            List of RiskItem objects
        """
        risks = []
        sentences = self._split_sentences(text)
        
        for sentence in sentences:
            for category, patterns in self.risk_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        severity = self._determine_severity(sentence)
                        risks.append(RiskItem(
                            description=self._extract_risk_description(sentence),
                            category=category,
                            severity=severity,
                            source_text=sentence,
                            confidence=0.8
                        ))
                        break  # One match per sentence per category
        
        return risks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _determine_severity(self, text: str) -> str:
        """Determine risk severity from context"""
        text_lower = text.lower()
        
        for severity, indicators in self.severity_indicators.items():
            for ind in indicators:
                if ind in text_lower:
                    return severity
        
        return 'medium'  # Default
    
    def _extract_risk_description(self, sentence: str) -> str:
        """Extract concise risk description"""
        # Remove common prefixes
        prefixes = ['there is a', 'we have a', 'this is a', 'note that']
        description = sentence
        for prefix in prefixes:
            if description.lower().startswith(prefix):
                description = description[len(prefix):].strip()
        
        # Truncate if too long
        if len(description) > 150:
            description = description[:147] + '...'
        
        return description
    
    def extract_action_items(self, text: str) -> List[ActionItem]:
        """
        Extract action items from document
        
        Args:
            text: Document text
            
        Returns:
            List of ActionItem objects
        """
        action_items = []
        sentences = self._split_sentences(text)
        
        action_patterns = [
            r'(?:please|kindly)\s+(\w+.*?)(?:\.|$)',
            r'(?:action\s+required|action\s+item)[:\s]+(.+?)(?:\.|$)',
            r'(?:must|shall|will|should)\s+(\w+.*?)(?:\.|$)',
            r'(?:ensure|verify|confirm|review|complete|submit)\s+(.+?)(?:\.|$)'
        ]
        
        assignee_pattern = r'(?:assigned\s+to|owner|responsible)[:\s]+(\w+(?:\s+\w+)?)'
        date_pattern = r'(?:by|due|deadline)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+\s+\d{1,2})'
        
        for sentence in sentences:
            for pattern in action_patterns:
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    # Extract assignee if mentioned
                    assignee_match = re.search(assignee_pattern, sentence, re.IGNORECASE)
                    assignee = assignee_match.group(1) if assignee_match else None
                    
                    # Extract due date if mentioned
                    date_match = re.search(date_pattern, sentence, re.IGNORECASE)
                    due_date = date_match.group(1) if date_match else None
                    
                    # Determine priority
                    priority = self._determine_priority(sentence)
                    
                    action_items.append(ActionItem(
                        description=match.group(1).strip() if match.group(1) else sentence,
                        assignee=assignee,
                        due_date=due_date,
                        priority=priority,
                        source_text=sentence
                    ))
                    break  # One action per sentence
        
        return action_items
    
    def _determine_priority(self, text: str) -> str:
        """Determine action item priority"""
        text_lower = text.lower()
        
        if any(ind in text_lower for ind in ['urgent', 'asap', 'immediately', 'critical']):
            return 'high'
        elif any(ind in text_lower for ind in ['soon', 'priority', 'important']):
            return 'medium'
        else:
            return 'normal'


# ============================================
# Contract Clause Analyzer
# ============================================

class ContractAnalyzer:
    """
    Analyzes construction contract clauses
    
    Identifies:
    - Key contract terms
    - Risk allocation clauses
    - Payment terms
    - Change order procedures
    - Dispute resolution mechanisms
    """
    
    def __init__(self):
        self.clause_patterns = {
            'payment': [
                r'payment\s+(?:terms|schedule|conditions)',
                r'(?:progress|final)\s+payment',
                r'retainage|retention',
                r'invoice|billing'
            ],
            'change_order': [
                r'change\s+order\s+(?:process|procedure)',
                r'(?:scope|contract)\s+(?:change|modification)',
                r'(?:written|prior)\s+(?:approval|authorization)'
            ],
            'indemnification': [
                r'indemnif(?:y|ication)',
                r'hold\s+harmless',
                r'defend\s+and\s+indemnify'
            ],
            'insurance': [
                r'insurance\s+(?:requirements|coverage)',
                r'(?:liability|workers\s+comp)\s+insurance',
                r'certificate\s+of\s+insurance'
            ],
            'warranty': [
                r'warrant(?:y|ies)',
                r'(?:defect|correction)\s+period',
                r'guarantee'
            ],
            'termination': [
                r'termination\s+(?:for|clause)',
                r'(?:default|breach)\s+(?:and|termination)',
                r'right\s+to\s+terminate'
            ],
            'dispute': [
                r'dispute\s+resolution',
                r'(?:arbitration|mediation)',
                r'claims\s+(?:process|procedure)'
            ],
            'liquidated_damages': [
                r'liquidated\s+damages',
                r'delay\s+damages',
                r'penalty\s+(?:clause|for)'
            ]
        }
    
    def analyze_contract(self, text: str) -> Dict[str, Any]:
        """
        Analyze contract document
        
        Args:
            text: Contract text
            
        Returns:
            Analysis results with identified clauses
        """
        results = {
            'identified_clauses': [],
            'risk_items': [],
            'key_terms': [],
            'recommendations': []
        }
        
        # Split into sections/paragraphs
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if len(para.strip()) < 20:
                continue
            
            for clause_type, patterns in self.clause_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, para, re.IGNORECASE):
                        results['identified_clauses'].append({
                            'type': clause_type,
                            'text': para[:500] + ('...' if len(para) > 500 else ''),
                            'pattern_matched': pattern
                        })
                        
                        # Check for risk indicators
                        risk = self._assess_clause_risk(para, clause_type)
                        if risk:
                            results['risk_items'].append(risk)
                        
                        break
        
        # Extract key terms
        results['key_terms'] = self._extract_key_terms(text)
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _assess_clause_risk(self, clause_text: str, clause_type: str) -> Optional[Dict]:
        """Assess risk level of a clause"""
        risk_indicators = {
            'indemnification': [
                ('broad', 'Broad indemnification language'),
                ('all claims', 'Unlimited liability scope'),
                ('sole', 'One-sided indemnification')
            ],
            'liquidated_damages': [
                ('per day', 'Daily liquidated damages'),
                ('unlimited', 'No cap on damages'),
                ('consequential', 'Consequential damages included')
            ],
            'termination': [
                ('without cause', 'Termination without cause allowed'),
                ('sole discretion', 'Unilateral termination rights'),
                ('immediate', 'Immediate termination possible')
            ]
        }
        
        indicators = risk_indicators.get(clause_type, [])
        text_lower = clause_text.lower()
        
        for keyword, description in indicators:
            if keyword in text_lower:
                return {
                    'clause_type': clause_type,
                    'risk_description': description,
                    'recommendation': f'Review {clause_type} clause for potential risk'
                }
        
        return None
    
    def _extract_key_terms(self, text: str) -> List[Dict]:
        """Extract key contractual terms"""
        terms = []
        
        # Dollar amounts
        amounts = re.findall(r'\$[\d,]+(?:\.\d{2})?', text)
        for amount in set(amounts):
            terms.append({'type': 'amount', 'value': amount})
        
        # Percentages
        percentages = re.findall(r'\d+(?:\.\d+)?%', text)
        for pct in set(percentages):
            terms.append({'type': 'percentage', 'value': pct})
        
        # Dates
        dates = re.findall(
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            text
        )
        for date in set(dates):
            terms.append({'type': 'date', 'value': date})
        
        # Duration periods
        durations = re.findall(
            r'\d+\s+(?:day|week|month|year)s?',
            text, re.IGNORECASE
        )
        for dur in set(durations):
            terms.append({'type': 'duration', 'value': dur})
        
        return terms[:20]  # Limit results
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        clause_types = [c['type'] for c in analysis['identified_clauses']]
        
        # Check for missing important clauses
        important_clauses = ['payment', 'change_order', 'insurance', 'warranty']
        missing = [c for c in important_clauses if c not in clause_types]
        
        for clause in missing:
            recommendations.append(
                f"Consider adding {clause.replace('_', ' ')} provisions"
            )
        
        # Add risk-based recommendations
        for risk in analysis['risk_items']:
            recommendations.append(risk['recommendation'])
        
        return recommendations[:10]


# ============================================
# Integrated NLP System
# ============================================

class ConstructionNLPSystem:
    """
    Integrated NLP system for construction document analysis
    
    Combines all NLP capabilities into a single interface
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.classifier = DocumentClassifier(model_path)
        self.ner = ConstructionNER(model_path)
        self.sentiment_analyzer = CommunicationAnalyzer(model_path)
        self.summarizer = DocumentSummarizer(model_path)
        self.risk_extractor = RiskIssueExtractor()
        self.contract_analyzer = ContractAnalyzer()
    
    def analyze_document(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive document analysis
        
        Args:
            text: Document text
            
        Returns:
            Complete analysis results
        """
        # Classify document
        classification = self.classifier.classify(text)
        
        # Extract entities
        entities = self.ner.extract_entities(text)
        
        # Analyze sentiment
        sentiment = self.sentiment_analyzer.analyze_sentiment(text)
        urgency = self.sentiment_analyzer.analyze_urgency(text)
        
        # Generate summary
        summary = self.summarizer.summarize(text)
        key_points = self.summarizer.extract_key_points(text)
        
        # Extract risks and action items
        risks = self.risk_extractor.extract_risks(text)
        action_items = self.risk_extractor.extract_action_items(text)
        
        # Contract analysis if applicable
        contract_analysis = None
        if classification.document_type == DocumentType.CONTRACT:
            contract_analysis = self.contract_analyzer.analyze_contract(text)
        
        return {
            'classification': asdict(classification),
            'entities': [asdict(e) for e in entities],
            'sentiment': asdict(sentiment),
            'urgency': urgency.value,
            'summary': summary,
            'key_points': key_points,
            'risks': [asdict(r) for r in risks],
            'action_items': [asdict(a) for a in action_items],
            'contract_analysis': contract_analysis,
            'analyzed_at': datetime.utcnow().isoformat(),
            'character_count': len(text),
            'word_count': len(text.split())
        }
    
    def batch_analyze(self, documents: List[Dict]) -> List[Dict]:
        """
        Analyze multiple documents
        
        Args:
            documents: List of {'id': str, 'text': str}
            
        Returns:
            List of analysis results
        """
        results = []
        for doc in documents:
            analysis = self.analyze_document(doc['text'])
            analysis['document_id'] = doc.get('id', 'unknown')
            results.append(analysis)
        
        return results


# Convenience instance
nlp_system = ConstructionNLPSystem()