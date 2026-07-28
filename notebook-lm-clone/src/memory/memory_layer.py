import logging
import os
import time
from typing import Optional, Any, Dict, List
from dataclasses import dataclass
from datetime import datetime

from zep_cloud.client import Zep
from zep_crewai import ZepUserStorage
from crewai.memory.external.external_memory import ExternalMemory
from src.generation.rag import RAGResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """Represents a single conversation turn with context"""
    user_query: str
    assistant_response: str
    sources_used: List[Dict[str, Any]]
    timestamp: str
    session_id: str

class DummyMemory:
    def save(self, *args, **kwargs):
        return None


class NotebookMemoryLayer:
    def __init__(
        self,
        user_id: str,
        session_id: str,
        zep_api_key: Optional[str] = None,
        mode: str = "summary",
        indexing_wait_time: int = 10,
        create_new_session: bool = False
    ):
        self.user_id = user_id
        self.session_id = session_id
        self.indexing_wait_time = indexing_wait_time
        self.external_memory = DummyMemory()
        logger.warning("Zep disabled — using DummyMemory (no persistence)")

        logger.info(f"NotebookMemoryLayer initialized for user {user_id}, session {session_id}")
    
    
    
    def save_conversation_turn(
        self,
        rag_result: RAGResult,
        user_metadata: Optional[Dict[str, Any]] = None,
        assistant_metadata: Optional[Dict[str, Any]] = None
    ):
        try:
            user_meta = {
                "type": "message",
                "role": "user", 
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                **(user_metadata or {})
            }
            
            # Save user message
            self.external_memory.save(
                rag_result.query,
                metadata=user_meta
            )
            
            assistant_meta = {
                "type": "message",
                "role": "assistant",
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "sources_count": len(rag_result.sources_used),
                "retrieval_count": rag_result.retrieval_count,
                "model_used": getattr(rag_result, 'model_name', 'unknown'),
                "sources_summary": self._create_sources_summary(rag_result.sources_used),
                **(assistant_metadata or {})
            }
            
            # Save assistant response
            self.external_memory.save(
                rag_result.response,
                metadata=assistant_meta
            )
            self._save_source_context(rag_result.sources_used)
            
            logger.info(f"Saved conversation turn with {len(rag_result.sources_used)} sources")
            
        except Exception as e:
            logger.error(f"Error saving conversation turn: {str(e)}")
            raise
    
    def _create_sources_summary(self, sources_used: List[Dict[str, Any]]) -> str:
        if not sources_used:
            return "No sources used"
        
        source_files = list(set(source.get('source_file', 'Unknown') for source in sources_used))
        source_types = list(set(source.get('source_type', 'unknown') for source in sources_used))
        
        summary = f"{len(source_files)} files ({', '.join(source_types)}): {', '.join(source_files[:3])}"
        if len(source_files) > 3:
            summary += f" and {len(source_files) - 3} more"
        
        return summary
    
    def _save_source_context(self, sources_used: List[Dict[str, Any]]):
        if not sources_used:
            return
        
        source_context = {
            "referenced_documents": [],
            "document_types": set(),
            "key_topics_discussed": []
        }
        
        for source in sources_used:
            doc_info = {
                "file": source.get('source_file', 'Unknown'),
                "type": source.get('source_type', 'unknown'),
                "page": source.get('page_number'),
                "relevance": source.get('relevance_score', 0)
            }
            source_context["referenced_documents"].append(doc_info)
            source_context["document_types"].add(doc_info["type"])
        
        source_context["document_types"] = list(source_context["document_types"])
        
        self.external_memory.save(
            f"Document sources referenced: {source_context}",
            metadata={
                "type": "source_context",
                "category": "document_usage",
                "session_id": self.session_id
            }
        )
    
    def save_user_preferences(self, preferences: Dict[str, Any]):
        try:
            self.external_memory.save(
                f"User preferences: {preferences}",
                metadata={
                    "type": "preferences",
                    "category": "user_settings",
                    "timestamp": datetime.now().isoformat(),
                    "session_id": self.session_id
                }
            )
            logger.info("User preferences saved to memory")
            
        except Exception as e:
            logger.error(f"Error saving preferences: {str(e)}")
    
    def save_document_metadata(self, document_info: Dict[str, Any]):
        try:
            self.external_memory.save(
                f"Document processed: {document_info}",
                metadata={
                    "type": "document_metadata",
                    "category": "system_events",
                    "timestamp": datetime.now().isoformat(),
                    "session_id": self.session_id
                }
            )
            logger.info(f"Document metadata saved: {document_info.get('name', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error saving document metadata: {str(e)}")
    
    def get_conversation_context(self) -> str:
        return ""
    def get_relevant_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        return []
    
    def wait_for_indexing(self):
        logger.info(f"Waiting {self.indexing_wait_time}s for Zep indexing...")
        time.sleep(self.indexing_wait_time)
    
    def get_session_summary(self) -> Dict[str, Any]:
        return {
        "session_id": self.session_id,
        "user_id": self.user_id,
        "memory": "disabled"
    }
    
    def clear_session(self):
        logger.info("Session cleared (dummy)")

if __name__ == "__main__":
    from src.generation.rag import RAGGenerator, RAGResult
    
    memory = NotebookMemoryLayer(
        user_id="test_user",
        session_id="test_session_123",
        create_new_session=True
    )
    
    try:
        mock_rag_result = RAGResult(
            query="What are the main findings in the research?",
            response="The research shows three key findings [1, 2]. First, the methodology was effective [1]. Second, the results were significant [2].",
            sources_used=[
                {"source_file": "research_paper.pdf", "source_type": "pdf", "page_number": 5},
                {"source_file": "data_analysis.pdf", "source_type": "pdf", "page_number": 12}
            ],
            retrieval_count=8
        )
        
        memory.save_conversation_turn(mock_rag_result)
        memory.wait_for_indexing()
        context = memory.get_conversation_context()
        print(f"Conversation Context:\n{context}")
        
        relevant = memory.get_relevant_memory("research findings")
        print(f"\nRelevant Memories: {len(relevant)} found")
        
        summary = memory.get_session_summary()
        print(f"\nSession Summary: {summary}")
        
        memory.save_user_preferences({
            "response_length": "detailed",
            "citation_style": "academic",
            "preferred_sources": ["pdf", "web"]
        })
        
        print("Memory integration test completed successfully")
        
    except Exception as e:
        print(f"Error in memory integration test: {e}")