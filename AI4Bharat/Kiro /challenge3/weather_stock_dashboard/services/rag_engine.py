"""LangChain RAG engine for natural language query processing."""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

try:
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    from langchain.schema import BaseRetriever, Document
    from langchain.llms.base import BaseLLM
    from langchain.llms import OpenAI
    from langchain.embeddings import OpenAIEmbeddings
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Mock classes for development
    class LLMChain:
        def __init__(self, **kwargs):
            pass
        def run(self, **kwargs):
            return "Mock LLM response"
    
    class PromptTemplate:
        def __init__(self, **kwargs):
            pass
    
    class BaseRetriever:
        def get_relevant_documents(self, query: str):
            return []
    
    class Document:
        def __init__(self, page_content: str, metadata: dict):
            self.page_content = page_content
            self.metadata = metadata

from config.settings import settings
from weather_stock_dashboard.services.chromadb_service import chromadb_service
from weather_stock_dashboard.services.query_fallback import query_fallback_handler, query_validator
from weather_stock_dashboard.models import NaturalLanguageQuery

logger = logging.getLogger(__name__)


class WeatherStockRetriever(BaseRetriever):
    """Custom retriever for weather-stock data from ChromaDB."""
    
    def __init__(self, chromadb_service):
        """Initialize retriever with ChromaDB service."""
        self.chromadb_service = chromadb_service
        
    def get_relevant_documents(self, query: str) -> List[Document]:
        """Retrieve relevant documents from ChromaDB."""
        try:
            # Perform hybrid search across all collections
            search_results = self.chromadb_service.hybrid_search(query, n_results=5)
            
            documents = []
            
            # Convert ChromaDB results to LangChain Documents
            for collection_name, results in search_results.items():
                for result in results:
                    doc = Document(
                        page_content=result["document"],
                        metadata={
                            "collection": collection_name,
                            "id": result["id"],
                            "distance": result["distance"],
                            **result["metadata"]
                        }
                    )
                    documents.append(doc)
            
            # Sort by relevance (lower distance = more relevant)
            documents.sort(key=lambda x: x.metadata.get("distance", float('inf')))
            
            return documents[:10]  # Return top 10 most relevant
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []


class QueryProcessor:
    """Process and classify natural language queries."""
    
    def __init__(self):
        """Initialize query processor."""
        self.intent_patterns = {
            "correlation": [
                r"correlat\w*", r"relationship", r"connection", r"association",
                r"how.*affect", r"impact", r"influence"
            ],
            "forecast": [
                r"predict\w*", r"forecast\w*", r"future", r"expect\w*",
                r"will.*be", r"trend", r"projection"
            ],
            "volatility": [
                r"volatil\w*", r"risk", r"fluctuat\w*", r"varianc\w*",
                r"unstable", r"swing\w*"
            ],
            "weather": [
                r"weather", r"temperature", r"rain\w*", r"snow\w*",
                r"storm\w*", r"climate", r"precipitation", r"humidity"
            ],
            "stock": [
                r"stock\w*", r"share\w*", r"market", r"price\w*",
                r"trading", r"equity", r"securities"
            ],
            "historical": [
                r"historical", r"past", r"previous", r"before",
                r"last.*year", r"ago", r"history"
            ],
            "comparison": [
                r"compar\w*", r"versus", r"vs", r"difference",
                r"better", r"worse", r"against"
            ]
        }
        
        self.entity_patterns = {
            "stock_symbols": r"\b[A-Z]{1,5}\b",  # Stock symbols (1-5 uppercase letters)
            "dates": r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b|\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b",
            "numbers": r"\b\d+\.?\d*\b",
            "locations": r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b"  # Capitalized words (potential locations)
        }
    
    def process_query(self, query_text: str) -> Dict[str, Any]:
        """Process natural language query and extract intent and entities."""
        try:
            query_lower = query_text.lower()
            
            # Intent classification
            intents = self._classify_intent(query_lower)
            
            # Entity extraction
            entities = self._extract_entities(query_text)
            
            # Query type determination
            query_type = self._determine_query_type(intents, entities)
            
            # Generate search terms
            search_terms = self._generate_search_terms(query_text, intents, entities)
            
            # Complexity assessment
            complexity = self._assess_query_complexity(query_text, intents, entities)
            
            return {
                "original_query": query_text,
                "intents": intents,
                "entities": entities,
                "query_type": query_type,
                "search_terms": search_terms,
                "complexity": complexity,
                "processed_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                "original_query": query_text,
                "intents": ["general"],
                "entities": {},
                "query_type": "general",
                "search_terms": [query_text],
                "complexity": "simple",
                "error": str(e)
            }
    
    def _classify_intent(self, query_lower: str) -> List[str]:
        """Classify query intent based on patterns."""
        detected_intents = []
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    detected_intents.append(intent)
                    break
        
        return detected_intents if detected_intents else ["general"]
    
    def _extract_entities(self, query_text: str) -> Dict[str, List[str]]:
        """Extract entities from query text."""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, query_text)
            if matches:
                entities[entity_type] = list(set(matches))  # Remove duplicates
        
        return entities
    
    def _determine_query_type(self, intents: List[str], entities: Dict[str, List[str]]) -> str:
        """Determine the type of query based on intents and entities."""
        if "correlation" in intents:
            if "weather" in intents and "stock" in intents:
                return "weather_stock_correlation"
            elif "weather" in intents:
                return "weather_analysis"
            elif "stock" in intents:
                return "stock_analysis"
            else:
                return "correlation_analysis"
        
        elif "forecast" in intents:
            if "weather" in intents:
                return "weather_forecast"
            elif "stock" in intents:
                return "stock_forecast"
            else:
                return "general_forecast"
        
        elif "volatility" in intents:
            return "volatility_analysis"
        
        elif "comparison" in intents:
            return "comparative_analysis"
        
        elif "historical" in intents:
            return "historical_analysis"
        
        else:
            return "general_inquiry"
    
    def _generate_search_terms(self, query_text: str, intents: List[str], entities: Dict[str, List[str]]) -> List[str]:
        """Generate search terms for document retrieval."""
        search_terms = []
        
        # Add original query
        search_terms.append(query_text)
        
        # Add intent-based terms
        for intent in intents:
            if intent == "correlation":
                search_terms.extend(["correlation", "relationship", "association"])
            elif intent == "forecast":
                search_terms.extend(["forecast", "prediction", "trend"])
            elif intent == "volatility":
                search_terms.extend(["volatility", "risk", "fluctuation"])
        
        # Add entity-based terms
        for entity_type, entity_list in entities.items():
            search_terms.extend(entity_list)
        
        # Remove duplicates and empty strings
        search_terms = list(set([term for term in search_terms if term.strip()]))
        
        return search_terms
    
    def _assess_query_complexity(self, query_text: str, intents: List[str], entities: Dict[str, List[str]]) -> str:
        """Assess the complexity of the query."""
        complexity_score = 0
        
        # Length factor
        if len(query_text.split()) > 15:
            complexity_score += 2
        elif len(query_text.split()) > 8:
            complexity_score += 1
        
        # Intent factor
        if len(intents) > 2:
            complexity_score += 2
        elif len(intents) > 1:
            complexity_score += 1
        
        # Entity factor
        total_entities = sum(len(entity_list) for entity_list in entities.values())
        if total_entities > 5:
            complexity_score += 2
        elif total_entities > 2:
            complexity_score += 1
        
        # Complex intent combinations
        if "correlation" in intents and "forecast" in intents:
            complexity_score += 1
        
        if complexity_score >= 4:
            return "complex"
        elif complexity_score >= 2:
            return "moderate"
        else:
            return "simple"


class RAGEngine:
    """Retrieval-Augmented Generation engine for weather-stock queries."""
    
    def __init__(self):
        """Initialize RAG engine."""
        self.query_processor = QueryProcessor()
        self.retriever = WeatherStockRetriever(chromadb_service)
        self.llm = None
        self.qa_chain = None
        
        if LANGCHAIN_AVAILABLE and settings.openai_api_key:
            try:
                self.llm = OpenAI(
                    openai_api_key=settings.openai_api_key,
                    temperature=0.1,
                    max_tokens=500
                )
                self._initialize_chains()
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI LLM: {e}")
        else:
            logger.warning("LangChain or OpenAI API key not available - using mock responses")
    
    def _initialize_chains(self):
        """Initialize LangChain chains for different query types."""
        # General QA chain
        qa_template = """
        You are an expert analyst specializing in weather-stock market correlations. 
        Use the following context to answer the question about weather and stock market relationships.
        
        Context: {context}
        
        Question: {question}
        
        Provide a clear, informative answer based on the context. If the context doesn't contain 
        enough information, say so and suggest what additional data might be helpful.
        
        Answer:"""
        
        self.qa_prompt = PromptTemplate(
            template=qa_template,
            input_variables=["context", "question"]
        )
        
        if self.llm:
            self.qa_chain = LLMChain(llm=self.llm, prompt=self.qa_prompt)
    
    async def process_query(self, query_text: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process natural language query and generate response."""
        try:
            # Validate and sanitize query
            validation_result = query_validator.validate_query(query_text)
            if not validation_result["is_valid"]:
                return {
                    "query": {"query_text": query_text, "validation_issues": validation_result["issues"]},
                    "response": query_fallback_handler.handle_processing_error(
                        query_text, Exception("Query validation failed")
                    )
                }
            
            sanitized_query = query_validator.sanitize_query(query_text)
            
            # Create query record
            query_record = NaturalLanguageQuery(
                query_text=sanitized_query,
                user_id=user_id,
                timestamp=datetime.utcnow()
            )
            
            # Process query to understand intent
            processed_query = self.query_processor.process_query(sanitized_query)
            
            # Check for complex or ambiguous queries
            if processed_query.get("complexity") == "complex":
                return {
                    "query": query_record.dict(),
                    "processed_query": processed_query,
                    "response": query_fallback_handler.handle_complex_query(sanitized_query, processed_query)
                }
            
            if len(processed_query.get("intents", [])) == 0:
                return {
                    "query": query_record.dict(),
                    "processed_query": processed_query,
                    "response": query_fallback_handler.handle_ambiguous_query(sanitized_query, processed_query)
                }
            
            # Retrieve relevant context
            context_docs = await self._retrieve_context(processed_query)
            
            # Handle no context case
            if not context_docs:
                return {
                    "query": query_record.dict(),
                    "processed_query": processed_query,
                    "response": query_fallback_handler.handle_no_context_error(sanitized_query, processed_query)
                }
            
            # Generate response
            response = await self._generate_response(processed_query, context_docs)
            
            # Update query record with results
            query_record.processed_intent = processed_query["query_type"]
            query_record.retrieved_context = [doc.page_content for doc in context_docs]
            
            return {
                "query": query_record.dict(),
                "processed_query": processed_query,
                "context_documents": len(context_docs),
                "response": response,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                "query": {"query_text": query_text, "error": str(e)},
                "response": query_fallback_handler.handle_processing_error(query_text, e)
            }
    
    async def _retrieve_context(self, processed_query: Dict[str, Any]) -> List[Document]:
        """Retrieve relevant context documents."""
        try:
            # Use search terms for retrieval
            search_terms = processed_query["search_terms"]
            all_docs = []
            
            # Retrieve documents for each search term
            for term in search_terms[:3]:  # Limit to top 3 search terms
                docs = self.retriever.get_relevant_documents(term)
                all_docs.extend(docs)
            
            # Remove duplicates based on document ID
            seen_ids = set()
            unique_docs = []
            for doc in all_docs:
                doc_id = doc.metadata.get("id", "")
                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    unique_docs.append(doc)
            
            # Sort by relevance and return top documents
            unique_docs.sort(key=lambda x: x.metadata.get("distance", float('inf')))
            return unique_docs[:5]  # Top 5 most relevant
            
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return []
    
    async def _generate_response(self, processed_query: Dict[str, Any], context_docs: List[Document]) -> Dict[str, Any]:
        """Generate response using LLM or fallback method."""
        try:
            if self.qa_chain and context_docs:
                # Use LangChain for response generation
                context_text = "\n\n".join([doc.page_content for doc in context_docs])
                
                response_text = self.qa_chain.run(
                    context=context_text,
                    question=processed_query["original_query"]
                )
                
                return {
                    "answer": response_text,
                    "confidence": "high",
                    "method": "llm_generated",
                    "context_used": len(context_docs)
                }
            else:
                # Fallback to template-based response
                return self._generate_template_response(processed_query, context_docs)
                
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return self._generate_template_response(processed_query, context_docs)
    
    def _generate_template_response(self, processed_query: Dict[str, Any], context_docs: List[Document]) -> Dict[str, Any]:
        """Generate template-based response when LLM is not available."""
        query_type = processed_query["query_type"]
        intents = processed_query["intents"]
        
        if not context_docs:
            return {
                "answer": "I don't have enough relevant data to answer your question about weather-stock relationships. Please try a more specific query or check if the data you're looking for has been collected.",
                "confidence": "low",
                "method": "template_no_context"
            }
        
        # Generate response based on query type
        if query_type == "weather_stock_correlation":
            answer = self._generate_correlation_response(context_docs)
        elif query_type == "weather_forecast":
            answer = self._generate_forecast_response(context_docs, "weather")
        elif query_type == "stock_forecast":
            answer = self._generate_forecast_response(context_docs, "stock")
        elif query_type == "volatility_analysis":
            answer = self._generate_volatility_response(context_docs)
        else:
            answer = self._generate_general_response(context_docs, processed_query)
        
        return {
            "answer": answer,
            "confidence": "medium",
            "method": "template_generated",
            "context_used": len(context_docs)
        }
    
    def _generate_correlation_response(self, context_docs: List[Document]) -> str:
        """Generate response for correlation queries."""
        correlation_docs = [doc for doc in context_docs if "correlation" in doc.metadata.get("type", "")]
        
        if correlation_docs:
            doc = correlation_docs[0]
            return f"Based on the analysis, {doc.page_content}. This correlation analysis is based on {len(context_docs)} relevant data points from our weather-stock database."
        else:
            return f"I found {len(context_docs)} relevant data points about weather and stock relationships. The analysis suggests there are observable patterns between weather conditions and market performance, though the specific correlation strength varies by sector and time period."
    
    def _generate_forecast_response(self, context_docs: List[Document], forecast_type: str) -> str:
        """Generate response for forecast queries."""
        forecast_docs = [doc for doc in context_docs if "forecast" in doc.page_content.lower()]
        
        if forecast_docs:
            doc = forecast_docs[0]
            return f"Based on time series analysis, {doc.page_content}. This forecast is generated from {len(context_docs)} relevant historical data points."
        else:
            return f"I found {len(context_docs)} relevant data points for {forecast_type} forecasting. While I can see historical patterns, I'd need more specific time series data to provide detailed forecasts."
    
    def _generate_volatility_response(self, context_docs: List[Document]) -> str:
        """Generate response for volatility queries."""
        volatility_docs = [doc for doc in context_docs if "volatility" in doc.page_content.lower()]
        
        if volatility_docs:
            doc = volatility_docs[0]
            return f"Regarding market volatility, {doc.page_content}. This analysis is based on {len(context_docs)} relevant data points from volatility modeling."
        else:
            return f"I found {len(context_docs)} relevant data points about market volatility. The analysis indicates varying volatility patterns that may be influenced by weather conditions, though specific relationships require detailed statistical analysis."
    
    def _generate_general_response(self, context_docs: List[Document], processed_query: Dict[str, Any]) -> str:
        """Generate general response."""
        if context_docs:
            most_relevant = context_docs[0]
            return f"Based on the available data, {most_relevant.page_content}. This information comes from our analysis of {len(context_docs)} relevant data points in the weather-stock correlation database."
        else:
            return "I don't have specific data to answer your question. Please try asking about weather-stock correlations, volatility analysis, or forecasting with more specific parameters."


# Global RAG engine instance
rag_engine = RAGEngine()