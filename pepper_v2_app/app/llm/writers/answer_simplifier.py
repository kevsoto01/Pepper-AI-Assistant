class AnswerSimplifier:
    def __init__(self, model):
        self.model = model
        self.system_instruction = """
        You are a strict simplifier. 
        
        Another LLM has determined that the provided answer to the provided question is too complex for a(n) {age} year old to understand. 
        Simplify the provided answer by reducing vocabulary complexity and sentence length. 
        
        Do not make the answer more fun.
        Do not add examples.
        Do not add new ideas.
        Do not add analogies.
        Do not change the meaning.
        Do not introduce yourself.
        Do not add greetings unless the original answer already has one.
        Do not describe your rules, limitations, or role instructions.
        
        Ensure that the modified answer still answers the original question.
        """
    
    def simplify(self, user_text, assistant_text, age:int) -> str:
        text = self._concatinate_user_and_assistant_text(user_text, assistant_text)
        prompt = self.model.generate_prompt(text, self.system_instruction.format(age=age))
        simplified_answer = self.model.generate_response(prompt)
        return simplified_answer
    
    def _concatinate_user_and_assistant_text(self, user_text, assistant_text):
        return f"""
        Question: {user_text}
        Answer: {assistant_text}
        """