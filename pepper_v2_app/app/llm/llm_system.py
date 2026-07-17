
# Import Writers
from .writers.answer_generator import AnswerGenerator
from .writers.answer_simplifier import AnswerSimplifier
from .writers.rag_query_optimizer import RagQueryOptimizer

# Import Judges
from .judges.safety_verifier import ChildSafetyVerifier
from .judges.answer_complexity_classifier import AnswerComplexityClassifier
from .judges.response_movement_router import ResponseMovementRouter
from .judges.birthday_request_classifier import BirthdaySongRequestClassifier
from .judges.rag_need_classifier import RagNeedClassifier

# Import RAG Engine
from .rag.qdrant_db_rag import GeneralKnowledgeRAG

from .llm_launcher import OllamaLauncher
# from .fact_verifier import FactVerifier
# from .question_router import QuestionRouter
# from .simplification_verifier import SimplificationVerifier

class LLMSystem:
    def __init__(self, model_hub):
        self.models = model_hub
    
    def load(self, writer_model:str, judge_model:str) -> None:
        print("Loading LLM system...")
        self.launcher = OllamaLauncher(use_vulkan=True, force_restart=True)
        self.launcher.start_ollama()
        self.models.load(writer_model, judge_model)

        writer = self.models.writer     # qwen2.5:3b
        judge = self.models.judge       # qwen2.5:1.5b
        
        self.answer_generator = AnswerGenerator(writer)
        self.answer_simplifier = AnswerSimplifier(writer)
        self.rag_query_optimizer = RagQueryOptimizer(writer)
        
        self.birthday_classifier = BirthdaySongRequestClassifier(judge)
        self.movement_classifier = ResponseMovementRouter(judge)
        self.child_safety_verifier = ChildSafetyVerifier(judge)
        self.complexity_classifier = AnswerComplexityClassifier(judge)
        self.rag_need_classifier = RagNeedClassifier(judge)

        self.rag = GeneralKnowledgeRAG()

        print("LLM system ready.")
        
    def unload(self) -> None:
        self.models.unload()

        
