"""
DONT USE
"""

class RagNeedClassifier:
    def __init__(self, model):
        self.model = model

        self.system_instruction = """
            You are a routing classifier for a K-8 educational assistant.

            Decide whether the student's question requires searching a knowledge database.

            Return exactly one of these:

            RAG
            NO_RAG

            Return RAG when the question asks for factual knowledge about topics such as science, history, geography, civics, people, animals, health, technology, art, or culture.

            Also return RAG when the answer depends on specific facts, dates, names, places, definitions, events, or detailed explanations.

            Return NO_RAG when the question involves:

            - Simple arithmetic
            - Logic using only information in the question
            - Creative writing
            - Rewriting or grammar help
            - Translation
            - Brainstorming
            - Personal opinions
            - Casual conversation

            When uncertain, return RAG.

            Do not explain your decision. Do not return punctuation or additional text.
        """
        
    def classify_rag_need(self, user_text) -> str:
        prompt = self.model.generate_prompt(user_text, self.system_instruction)
        rag_classification = self.model.generate_response(prompt)
    
        print("RAG classifier output: '{}'".format(rag_classification))
    
        parsed_rag_classification = self.parse_rag_label(rag_classification)
        return parsed_rag_classification
    
    def parse_rag_label(self, raw_output: str) -> str:
        if not raw_output:
            return "RAG"
    
        lines = raw_output.strip().splitlines()
    
        for line in lines:
            clean = line.strip().upper()
    
            if clean == "RAG":
                return "RAG"
    
            if clean == "NO_RAG":
                return "NO_RAG"
    
        return "RAG"
        
    
