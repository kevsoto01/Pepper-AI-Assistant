"""
DONT USE
"""

class RagQualityClassifier:
    def __init__(self, model):
        self.model = model
        self.system_instruction = """
            You are a strict RAG quality classifier.
            
            You read:
            1. A question asked by a student.
            2. Retrieved context from a database, knowledge base, document, or lesson.
            
            Your job is to decide whether the retrieved context is useful enough to answer the student's question.
            
            Classify as GOOD_CONTEXT if the retrieved context:
            - directly answers the student's question
            - contains the main facts needed to answer
            - is clearly related to the question
            - provides enough information to ground the answer
            - should be used by the assistant when answering
            
            Classify as BAD_CONTEXT if the retrieved context:
            - is empty
            - is unrelated to the question
            - only matches a few random words
            - does not contain the facts needed to answer
            - is too vague to support an answer
            - could cause the assistant to give an incorrect or unsupported answer
            - should be ignored when answering
            
            Do not answer the student's question.
            Do not explain your decision.
            Do not rewrite the context.
            Do not judge whether the context is written simply.
            Do not judge whether the context is interesting.
            Do not classify based on the student's age.
            
            Return only one word:
            
            GOOD_CONTEXT
            
            or
            
            BAD_CONTEXT
            """
        
    def classify_context_quality(self, user_text: str, retrieved_context: str) -> str:
        classifier_input = f"""
            Student question:
            {user_text}
            
            Retrieved context:
            {retrieved_context}
            """
        prompt = self.model.generate_prompt(classifier_input, self.system_instruction)
        quality_classification = self.model.generate_response(prompt)
        print("RAG quality classifier output: '{}'".format(quality_classification))

        return self.parse_quality_label(quality_classification)

    def is_good_context(self, user_text: str, retrieved_context: str) -> bool:
        label = self.classify_context_quality(user_text, retrieved_context)
        return label == "GOOD_CONTEXT"

    def parse_quality_label(self, raw_output: str) -> str:
        if not raw_output:
            return "BAD_CONTEXT"

        lines = raw_output.strip().splitlines()

        for line in lines:
            clean = line.strip().upper()

            if clean == "GOOD_CONTEXT":
                return "GOOD_CONTEXT"

            if clean == "BAD_CONTEXT":
                return "BAD_CONTEXT"

        return "BAD_CONTEXT"
        
    
