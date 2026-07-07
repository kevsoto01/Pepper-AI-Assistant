class ResponseMovementRouter:
    def __init__(self, model, allowed_movements=None):
        self.model = model

        self.allowed_movements = allowed_movements or [
            "none",
            "body_talk",
            "wave",
            "happy",
            "thinking",
        ]

        self.default_movement = "body_talk"

        self.system_instruction = """
            You are a strict movement router for a Pepper robot.

            Your job is to choose the single best movement Pepper should make while the assistant gives a response.

            Allowed movements:
            {allowed_movements}

            Movement meanings:
            - none: Pepper should stay still.
            - body_talk: Pepper should make small natural speaking movements.
            - wave: Pepper should wave.
            - happy: Pepper should make a positive or celebratory movement.
            - thinking: Pepper should make a thinking-style movement.

            Decision rules:
            - Return only one allowed movement name.
            - Do not explain your answer.
            - Do not add punctuation.
            - Do not add extra words.
            - Use "none" if the response is serious, sensitive, unsafe, medical, sad, or emotionally heavy.
            - Use "wave" only if the response is mainly a greeting, goodbye, or welcome message.
            - If the response starts with a greeting but then answers a question, do not choose "wave" because of the greeting. Choose based on the main answer.
            - Use "happy" only if the main response is clearly positive, celebratory, encouraging, or congratulatory.
            - Use "thinking" only if the main response is explaining, reasoning, calculating, comparing, or teaching.
            - Use "body_talk" for normal conversational responses that do not fit the other movement types.
            """

    def classify_movement(
        self,
        assistant_text: str,
        user_text: str = "",
    ) -> str:
        system_instruction = self.system_instruction.format(
            allowed_movements=", ".join(self.allowed_movements)
        )

        input_text = self._build_input_text(
            user_text=user_text,
            assistant_text=assistant_text,
        )

        prompt = self.model.generate_prompt(
            input_text,
            system_instruction,
        )

        raw_movement = self.model.generate_response(prompt)

        return self._clean_movement(raw_movement)

    def _build_input_text(self, user_text: str, assistant_text: str) -> str:
        if user_text:
            return f"""
            User question:
            {user_text}

            Assistant response:
            {assistant_text}
            """

        return f"""
            Assistant response:
            {assistant_text}
            """

    def _clean_movement(self, raw_movement: str) -> str:
        movement = raw_movement.strip().lower()

        movement = movement.replace("`", "")
        movement = movement.replace(".", "")
        movement = movement.replace(",", "")
        movement = movement.replace(":", "")
        movement = movement.strip()

        if movement in self.allowed_movements:
            return movement

        return self.default_movement