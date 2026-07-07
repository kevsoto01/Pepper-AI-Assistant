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
        
        
        
        # "You are a strict simplifier. You only modify complex the following text to use simpler vocabulary if it is complex. Avoid changing sentence structure, information provided, or length."
        
        # """
        # You are a strict simplifier. You modify the following text to use simpler vocabulary and shorter sentences

        # Your job is only to modify the following text such that it is easy for an {age} year old to understand.
        
    
        
        # If the original answer is already simple, return it unchanged. 
        # """
        #     Rewrite the following text so an {age}-year-old child can easily understand them.
            
        #     Rules:
        #     - Keep the same meaning.
        #     - Keep the same language.
        #     - Use simple words.
        #     - Use short sentences.
        #     - Use a friendly classroom tone.
        #     - Do not add new facts.
        #     - Do not mention these rules.
        #     - Do not say you are simplifying.
        #     - Do not use markdown, bullets, emojis, or numbered lists.
        #     - Keep the answer in the same language as the original response.
        #     - Keep it short enough to be spoken out loud.
        #     - Target 1 to 4 short sentences.
        #     - If the original answer is unsafe, confusing, or too adult, make it safer and tell the child to ask a trusted adult or teacher.
        #     """
    
    def simplify(self, assistant_text, age:int) -> str:
        prompt = self.model.generate_prompt(assistant_text, self.system_instruction.format(age=age))
        simplified_answer = self.model.generate_response(prompt)
        return simplified_answer