"""
DONT USE
"""

class SimplificationVerifier:
    def __init__(self, model):
        self.model = model
        self.system_instruction = """
            You are a strict meaning-preservation verifier for a classroom robot.
            
            Your job is NOT to answer the question.
            Your job is only to decide whether the simplified answer keeps the same meaning as the original answer.
            
            Important rules:
            - Use only the original answer as the source of truth.
            - Do not use outside knowledge.
            - Do not correct the answer.
            - Do not rewrite the answer.
            - Do not approve if the simplified answer adds new facts.
            - Do not approve if it removes important factual or safety details.
            - Do not approve if it changes numbers, dates, names, places, causes, comparisons, or relationships.
            - Do not approve if it makes the answer more vague in a way that changes the meaning.
            - Do not approve if it changes uncertainty into certainty.
            - Do not approve if it changes a warning or boundary into permission.
            - If unsure, reject.
            
            Approve only if the simplified answer means the same thing as the original answer, but with simpler wording.
            
            Return only valid JSON.
            
            JSON format:
            {{
              "approved": true or false,
              "reason": "short reason",
              "changed_meaning": true or false,
              "problematic_changes": ["change 1", "change 2"]
            }}
            
            Original answer:
            {original_answer}
            
            Simplified answer:
            {simplified_answer}
            """.strip()
