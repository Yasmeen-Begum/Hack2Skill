"""Fallback mechanisms and error handling for query processing."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class QueryFallbackHandler:
    """Handle query processing fallbacks and error recovery."""
    
    def __init__(self):
        """Initialize fallback handler."""
        self.fallback_responses = {
            "no_context": [
                "I don't have enough relevant data to answer your specific question. Could you try asking about general weather-stock correlations or provide more context?",
                "I couldn't find specific information about that topic in our database. Try asking about temperature effects on stock prices or volatility patterns.",
                "The data I have doesn't contain enough information to answer that question. Consider asking about historical weather-market relationships."
            ],
            "processing_error": [
                "I encountered an issue processing your query. Please try rephrasing your question or asking about a specific weather-stock relationship.",
                "There was a technical issue with your request. Try asking about correlations between weather patterns and market performance.",
                "I'm having trouble understanding that query. Could you ask about weather impacts on specific stocks or sectors?"
            ],
            "complex_query": [
                "That's a complex question that might require breaking down into smaller parts. Try asking about one specific aspect of weather-stock relationships.",
                "Your question covers multiple topics. Consider asking about weather correlations, volatility analysis, or forecasting separately.",
                "That's quite comprehensive! Let's start with a specific aspect - are you interested in correlations, forecasts, or volatility analysis?"
            ],
            "ambiguous_query": [
                "Your question could be interpreted in several ways. Are you asking about weather-stock correlations, market forecasting, or volatility analysis?",
                "I need a bit more clarity. Are you interested in how weather affects stock prices, volatility patterns, or something else?",
                "Could you be more specific? I can help with weather-stock correlations, time series forecasting, or market volatility analysis."
            ]
        }
        
        self.suggestion_templates = {
            "correlation": [
                "How does temperature affect stock prices?",
                "What's the correlation between rainfall and market volatility?",
                "Do weather patterns influence tech stock performance?"
            ],
            "forecast": [
                "What are the weather forecasts for next month?",
                "Can you predict stock price trends based on weather?",
                "What's the forecast for AAPL stock price?"
            ],
            "volatility": [
                "How does weather affect market volatility?",
                "What causes stock price fluctuations during storms?",
                "Analyze volatility patterns in energy stocks during winter."
            ],
            "general": [
                "Show me weather-stock correlations for the past year",
                "How do seasonal patterns affect the stock market?",
                "What weather factors most influence financial markets?"
            ]
        }
    
    def handle_no_context_error(self, query: str, processed_query: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cases where no relevant context is found."""
        try:
            # Analyze why no context was found
            analysis = self._analyze_no_context_cause(query, processed_query)
            
            # Select appropriate fallback response
            response_text = random.choice(self.fallback_responses["no_context"])
            
            # Add suggestions based on query intent
            suggestions = self._generate_suggestions(processed_query.get("intents", []))
            
            return {
                "answer": response_text,
                "confidence": "low",
                "method": "no_context_fallback",
                "analysis": analysis,
                "suggestions": suggestions,
                "fallback_reason": "no_relevant_context"
            }
            
        except Exception as e:
            logger.error(f"Error in no_context_fallback: {e}")
            return self._generate_generic_fallback(query)
    
    def handle_processing_error(self, query: str, error: Exception) -> Dict[str, Any]:
        """Handle query processing errors."""
        try:
            error_type = self._classify_error(error)
            
            if error_type == "timeout":
                response_text = "The query is taking longer than expected to process. Please try a simpler question or try again later."
            elif error_type == "validation":
                response_text = "There seems to be an issue with the query format. Please check your question and try again."
            elif error_type == "resource":
                response_text = "I'm currently experiencing high load. Please try your question again in a moment."
            else:
                response_text = random.choice(self.fallback_responses["processing_error"])
            
            # Generate alternative suggestions
            suggestions = self._generate_general_suggestions()
            
            return {
                "answer": response_text,
                "confidence": "low",
                "method": "error_fallback",
                "error_type": error_type,
                "suggestions": suggestions,
                "fallback_reason": "processing_error"
            }
            
        except Exception as e:
            logger.error(f"Error in processing_error_fallback: {e}")
            return self._generate_generic_fallback(query)
    
    def handle_complex_query(self, query: str, processed_query: Dict[str, Any]) -> Dict[str, Any]:
        """Handle overly complex queries."""
        try:
            # Identify complexity factors
            complexity_factors = self._identify_complexity_factors(processed_query)
            
            # Generate response
            response_text = random.choice(self.fallback_responses["complex_query"])
            
            # Suggest breaking down the query
            breakdown_suggestions = self._suggest_query_breakdown(processed_query)
            
            return {
                "answer": response_text,
                "confidence": "medium",
                "method": "complexity_fallback",
                "complexity_factors": complexity_factors,
                "breakdown_suggestions": breakdown_suggestions,
                "fallback_reason": "query_too_complex"
            }
            
        except Exception as e:
            logger.error(f"Error in complex_query_fallback: {e}")
            return self._generate_generic_fallback(query)
    
    def handle_ambiguous_query(self, query: str, processed_query: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ambiguous queries."""
        try:
            # Identify ambiguity sources
            ambiguity_sources = self._identify_ambiguity_sources(processed_query)
            
            # Generate clarification response
            response_text = random.choice(self.fallback_responses["ambiguous_query"])
            
            # Suggest clarifications
            clarifications = self._suggest_clarifications(processed_query)
            
            return {
                "answer": response_text,
                "confidence": "medium",
                "method": "ambiguity_fallback",
                "ambiguity_sources": ambiguity_sources,
                "clarifications": clarifications,
                "fallback_reason": "query_ambiguous"
            }
            
        except Exception as e:
            logger.error(f"Error in ambiguous_query_fallback: {e}")
            return self._generate_generic_fallback(query)
    
    def _analyze_no_context_cause(self, query: str, processed_query: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze why no context was found."""
        analysis = {
            "query_length": len(query.split()),
            "intents_detected": len(processed_query.get("intents", [])),
            "entities_found": len(processed_query.get("entities", {})),
            "search_terms": len(processed_query.get("search_terms", []))
        }
        
        # Determine likely causes
        causes = []
        if analysis["intents_detected"] == 0:
            causes.append("No clear intent detected")
        if analysis["entities_found"] == 0:
            causes.append("No specific entities identified")
        if analysis["search_terms"] < 2:
            causes.append("Limited search terms generated")
        
        analysis["likely_causes"] = causes
        return analysis
    
    def _classify_error(self, error: Exception) -> str:
        """Classify the type of error."""
        error_str = str(error).lower()
        
        if "timeout" in error_str or "time" in error_str:
            return "timeout"
        elif "validation" in error_str or "invalid" in error_str:
            return "validation"
        elif "memory" in error_str or "resource" in error_str:
            return "resource"
        elif "connection" in error_str or "network" in error_str:
            return "network"
        else:
            return "unknown"
    
    def _generate_suggestions(self, intents: List[str]) -> List[str]:
        """Generate suggestions based on detected intents."""
        suggestions = []
        
        for intent in intents:
            if intent in self.suggestion_templates:
                suggestions.extend(self.suggestion_templates[intent][:2])
        
        # If no specific suggestions, use general ones
        if not suggestions:
            suggestions = self.suggestion_templates["general"][:3]
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _generate_general_suggestions(self) -> List[str]:
        """Generate general query suggestions."""
        all_suggestions = []
        for suggestions in self.suggestion_templates.values():
            all_suggestions.extend(suggestions)
        
        # Return random selection
        return random.sample(all_suggestions, min(3, len(all_suggestions)))
    
    def _identify_complexity_factors(self, processed_query: Dict[str, Any]) -> List[str]:
        """Identify what makes a query complex."""
        factors = []
        
        intents = processed_query.get("intents", [])
        entities = processed_query.get("entities", {})
        
        if len(intents) > 2:
            factors.append(f"Multiple intents detected: {', '.join(intents)}")
        
        total_entities = sum(len(entity_list) for entity_list in entities.values())
        if total_entities > 5:
            factors.append(f"Many entities mentioned: {total_entities} total")
        
        if processed_query.get("complexity") == "complex":
            factors.append("Complex language structure")
        
        return factors
    
    def _suggest_query_breakdown(self, processed_query: Dict[str, Any]) -> List[str]:
        """Suggest how to break down a complex query."""
        suggestions = []
        intents = processed_query.get("intents", [])
        
        if "correlation" in intents:
            suggestions.append("Ask about weather-stock correlations first")
        if "forecast" in intents:
            suggestions.append("Ask about forecasting separately")
        if "volatility" in intents:
            suggestions.append("Focus on volatility analysis alone")
        
        return suggestions
    
    def _identify_ambiguity_sources(self, processed_query: Dict[str, Any]) -> List[str]:
        """Identify sources of ambiguity in the query."""
        sources = []
        
        intents = processed_query.get("intents", [])
        entities = processed_query.get("entities", {})
        
        if len(intents) == 0:
            sources.append("No clear intent detected")
        elif len(intents) > 3:
            sources.append("Too many possible interpretations")
        
        if "stock_symbols" in entities and len(entities["stock_symbols"]) > 3:
            sources.append("Multiple stock symbols mentioned")
        
        if not entities:
            sources.append("No specific entities mentioned")
        
        return sources
    
    def _suggest_clarifications(self, processed_query: Dict[str, Any]) -> List[str]:
        """Suggest clarifications for ambiguous queries."""
        clarifications = []
        
        intents = processed_query.get("intents", [])
        
        if not intents or "general" in intents:
            clarifications.extend([
                "Are you asking about correlations between weather and stocks?",
                "Do you want forecasting information?",
                "Are you interested in volatility analysis?"
            ])
        
        entities = processed_query.get("entities", {})
        if not entities.get("stock_symbols"):
            clarifications.append("Which specific stocks or sectors are you interested in?")
        
        if not any(weather_term in processed_query.get("original_query", "").lower() 
                  for weather_term in ["weather", "temperature", "rain", "storm"]):
            clarifications.append("Which weather factors are you asking about?")
        
        return clarifications[:3]
    
    def _generate_generic_fallback(self, query: str) -> Dict[str, Any]:
        """Generate a generic fallback response."""
        return {
            "answer": "I apologize, but I'm having trouble processing your query. Please try asking about weather-stock correlations, forecasting, or volatility analysis with more specific details.",
            "confidence": "low",
            "method": "generic_fallback",
            "suggestions": self._generate_general_suggestions(),
            "fallback_reason": "generic_error"
        }


class QueryValidator:
    """Validate queries before processing."""
    
    def __init__(self):
        """Initialize query validator."""
        self.min_query_length = 3
        self.max_query_length = 500
        self.blocked_patterns = [
            r"hack\w*", r"exploit\w*", r"malicious", r"virus",
            r"password", r"login", r"admin"
        ]
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate query and return validation result."""
        try:
            validation_result = {
                "is_valid": True,
                "issues": [],
                "warnings": []
            }
            
            # Length validation
            if len(query.strip()) < self.min_query_length:
                validation_result["is_valid"] = False
                validation_result["issues"].append("Query too short")
            
            if len(query) > self.max_query_length:
                validation_result["is_valid"] = False
                validation_result["issues"].append("Query too long")
            
            # Content validation
            query_lower = query.lower()
            for pattern in self.blocked_patterns:
                import re
                if re.search(pattern, query_lower):
                    validation_result["is_valid"] = False
                    validation_result["issues"].append("Query contains blocked content")
                    break
            
            # Warning checks
            if not any(term in query_lower for term in ["weather", "stock", "market", "price", "volatility", "forecast"]):
                validation_result["warnings"].append("Query may not be related to weather-stock analysis")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Query validation failed: {e}")
            return {
                "is_valid": False,
                "issues": ["Validation error occurred"],
                "warnings": []
            }
    
    def sanitize_query(self, query: str) -> str:
        """Sanitize query text."""
        try:
            # Remove excessive whitespace
            sanitized = " ".join(query.split())
            
            # Remove potentially harmful characters
            import re
            sanitized = re.sub(r'[<>"\']', '', sanitized)
            
            # Limit length
            if len(sanitized) > self.max_query_length:
                sanitized = sanitized[:self.max_query_length] + "..."
            
            return sanitized
            
        except Exception as e:
            logger.error(f"Query sanitization failed: {e}")
            return query[:100]  # Fallback to truncated original


# Global instances
query_fallback_handler = QueryFallbackHandler()
query_validator = QueryValidator()