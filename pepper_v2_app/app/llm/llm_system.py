
# Import Writers
from .writers.answer_generator import AnswerGenerator
from .writers.answer_simplifier import AnswerSimplifier

# Import Judges
from .judges.safety_verifier import ChildSafetyVerifier
from .judges.answer_complexity_classifier import AnswerComplexityClassifier
from .judges.response_movement_router import ResponseMovementRouter
from .judges.birthday_request_classifier import BirthdaySongRequestClassifier

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

        writer = self.models.writer     # qwen2.5:1.5b
        judge = self.models.judge       # qwen2.5:3b
        
        self.answer_generator = AnswerGenerator(writer)
        self.answer_simplifier = AnswerSimplifier(writer)
        
        self.birthday_classifier = BirthdaySongRequestClassifier(judge)
        self.movement_classifier = ResponseMovementRouter(judge)
        self.child_safety_verifier = ChildSafetyVerifier(judge)
        self.complexity_classifier = AnswerComplexityClassifier(judge)

        print("LLM system ready.")
        
    def unload(self) -> None:
        self.models.unload()
    
    def answer_question(self, user_text, language):
        max_turns = 3#self.config_controller.get_setting("general", "max_turns")
        word_count = 30 #self.config_controller.get_setting("general", "word_count")
        return self.answer_generator.generate_response(user_text, language, max_turns, word_count)
        
    def simplify_answer(self, user_text, assistant_text):
        age = 100#self.config_controller.get_setting("general", "age")
        return self.answer_simplifier.simplify(assistant_text, age)
    
    def verify_safety(self, input_text):
        safety_classification = self.child_safety_verifier.check_safety(input_text)
        if safety_classification == "SAFE": return True
        if safety_classification == "UNSAFE": return False
        print("Unexpected safety classification, classifying as unsafe.")
        return False
    
    def is_answer_complex(self, user_text, assistant_text, age):
        answer_complexity = self.complexity_classifier.classify_complexity(user_text, assistant_text, age)
        if answer_complexity == "COMPLEX": return True
        if answer_complexity == "SIMPLE": return False
        print("Unexpected complexity classification, classifying as simple.")
        return False
    
    def should_sing_birthday_song(self, user_text):
        birthday_song_intent = self.birthday_classifier.check_happy_birthday_intent(user_text)
        print("birthday_song_intent:", birthday_song_intent)
        if birthday_song_intent == "SING": return True
        if birthday_song_intent == "OTHER": return False
        print("Unexpected birthday song intent classification, classifying as other.")
        return False

    def get_action(self, user_text):
        pseudocode = """

        if should_i_sing: return "SING"
        elif should_i_wave: return "WAVE"
        elif should_i_dance: return "DANCE"
        else: return "BODYTALK"
        
        """

        return "BODYTALK" # temporary

        
