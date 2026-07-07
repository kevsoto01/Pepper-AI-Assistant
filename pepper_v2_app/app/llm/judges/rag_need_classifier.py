"""
DONT USE
"""

class RagNeedClassifier:
    def __init__(self, model):
        self.model = model
        self.system_instruction = """
        You are a strict classifier.

        You read a question asked by a student.
        
        Your job is to decide whether answering the question requires retrieving factual information from a database, knowledge base, documents, or external source.
        
        Classify as RAG_REQUIRED if the answer depends on factual information that may need to be looked up, retrieved, verified, or grounded in stored knowledge.
        
        Classify as NO_RAG if the answer can be answered without retrieval, using only conversation, reasoning, rewriting, creativity, or general language ability.
        
        Use RAG_REQUIRED if the student asks about:
        
        * specific facts
        * definitions
        * historical events
        * science, math, geography, health, laws, rules, or current information
        * information from a textbook, article, document, lesson, database, or uploaded material
        * anything that needs verification
        * anything where accuracy depends on knowing the correct factual answer
        
        Use NO_RAG if the student asks for:
        
        * casual conversation
        * encouragement
        * opinions that do not depend on facts
        * rewriting, simplifying, translating, or correcting text
        * brainstorming
        * creative writing
        * explaining something already provided in the conversation
        * help with tone, wording, grammar, or style
        * a response that can be produced without checking facts
        
        Do not classify based on whether the question is easy or hard.
        Do not classify based on the student’s age.
        Do not classify based on whether the answer should be simplified.
        Do not answer the student’s question.
        Do not explain your decision.
        
        Return only one word:
        
        RAG_REQUIRED
        
        or
        
        NO_RAG

        """
        
    def classify_rag_need(self, user_text) -> str:
        prompt = self.model.generate_prompt(user_text, self.system_instruction)
        rag_classification = self.model.generate_response(prompt)
    
        print("RAG classifier output: '{}'".format(rag_classification))
    
        parsed_rag_classification = self.parse_rag_label(rag_classification)
        return parsed_rag_classification
    
    
    def parse_rag_label(self, raw_output: str) -> str:
        if not raw_output:
            return "RAG_REQUIRED"
    
        lines = raw_output.strip().splitlines()
    
        for line in lines:
            clean = line.strip().upper()
    
            if clean == "RAG_REQUIRED":
                return "RAG_REQUIRED"
    
            if clean == "NO_RAG":
                return "NO_RAG"
    
        return "RAG_REQUIRED"
        
    
