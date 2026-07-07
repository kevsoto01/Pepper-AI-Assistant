"""
USE
"""

class AnswerComplexityClassifier:
    def __init__(self, model):
        self.model = model
        self.system_instruction = """
        You are a strict classifier.
        
        You read:
        1. A question asked by a(n) {age} year old student.
        2. An answer provided by an LLM.
        
        Your job is to decide whether the answer needs to be simplified before being shown to the student.
        
        Classify the answer as SIMPLE only if it can be shown to a(n) {age} year old student without needing simplification.
        
        Classify the answer as COMPLEX if the answer should be sent to a simplifier that will:
        - reduce vocabulary complexity
        - shorten sentences
        - keep the same meaning
        - avoid adding examples
        - avoid adding analogies
        - avoid adding new ideas
        - avoid making the answer more fun
        
        Use COMPLEX if the answer:
        - uses words that may be too advanced for a(n) {age} year old
        - uses long or layered sentences
        - explains the idea in a way that feels too mature for the student's age
        - includes unnecessary detail
        - includes technical terms that are not explained simply
        - answers the question but is harder to understand than necessary
        - would benefit from shorter wording or simpler vocabulary
        
        Use SIMPLE if the answer:
        - uses clear, age-appropriate wording
        - uses short or easy-to-follow sentences
        - answers the original question directly
        - does not need easier vocabulary
        - does not need sentence shortening
        - is already understandable for a(n) {age} year old
        
        Do not judge whether the answer is fun, friendly, or interesting.
        Do not classify based on correctness unless the wording itself becomes confusing.
        Do not classify based on length alone.
        Do not rewrite the answer.
        Do not explain your decision.
        
        Return only one word:
        
        SIMPLE
        
        or
        
        COMPLEX
        """
        
    def classify_complexity(self, user_text, assistant_text, age) -> bool:
        prompt = self.model.generate_prompt(user_text, self.system_instruction.format(age=age))
        complexity_classification = self.model.generate_response(prompt)
        print("Complexity classifier output: '{}'".format(complexity_classification))
        parsed_complexity_classification = self.parse_complexity_label(complexity_classification)
        return parsed_complexity_classification
        
    def parse_complexity_label(self, raw_output: str) -> str:
        if not raw_output:
            return "SIMPLE"
    
        lines = raw_output.strip().splitlines()
    
        for line in lines:
            clean = line.strip().upper()
            if clean == "SIMPLE":
                return "SIMPLE"
            if clean == "COMPLEX":
                return "COMPLEX"
            
        return "SIMPLE"
        
    
