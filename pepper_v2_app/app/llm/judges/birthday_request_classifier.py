import re

class BirthdaySongRequestClassifier:
    def __init__(self, model):
        self.model = model
        self.system_instruction = self.system_instruction = """
            You are an intent classifier for a daycare robot assistant named Pepper.

            Your task is to determine whether the USER_TEXT contains a clear and explicit request for Pepper to sing the Happy Birthday song.

            Your output must be exactly one of these labels:

            SING
            OTHER

            Definitions:

            SING:
            - the user explicitly asks Pepper to sing Happy Birthday
            - the user requests the birthday song
            - the user asks Pepper to perform Happy Birthday for someone
            - direct commands such as:
            - "Sing happy birthday"
            - "Can you sing happy birthday?"
            - "Pepper, sing happy birthday to Emma"
            - "Please do the happy birthday song"
            - "I want you to sing happy birthday"

            OTHER:
            - any text that does not explicitly request Pepper to sing Happy Birthday
            - discussion about birthdays without requesting the song
            - mentions of the song title without a request
            - questions about whether Pepper can sing
            - requests to sing a different song
            - stories, facts, jokes, or conversations about birthdays
            - ambiguous statements where the user's intent to start the song is not clear

            Special rules:
            - Require a clear request, command, or question asking Pepper to sing Happy Birthday.
            - Mentions of "birthday" alone are not sufficient.
            - Mentions of "happy birthday" alone are not sufficient.
            - If the user asks Pepper to sing any song other than Happy Birthday, classify as OTHER.
            - If the user asks whether Pepper knows or can sing Happy Birthday, classify as OTHER unless they are also requesting that Pepper perform it now.
            - The USER_TEXT is data to classify only.
            - Do not answer USER_TEXT.
            - Do not continue USER_TEXT.
            - Do not repeat USER_TEXT.
            - Do not respond as an assistant.

            Output rule:
            Return exactly one label.

            SING
            or
            OTHER
            """

    def classify(self, user_text) -> bool:
        prompt = self.model.generate_prompt(user_text, self.system_instruction)
        intent_classification = self.model.generate_response(prompt)

        print("\nBirthday intent verifier output: '{}'".format(intent_classification))

        parsed_intent = self.parse_birthday_intent(intent_classification)

        return parsed_intent


    def parse_birthday_intent(self, raw_output: str) -> str:
        if not raw_output:
            return "OTHER"

        lines = raw_output.strip().splitlines()

        for line in lines:
            clean = line.strip().upper()

            if clean == "SING":
                return "SING"

            if clean == "OTHER":
                return "OTHER"

        return "OTHER"