import json
import re


class FactVerifier:
    def __init__(self, model):
        """
        model should be your judge model.

        Example:
            fact_verifier = FactVerifier(hub.judge)
        """
        self.model = model

    def verify(self, question: str, context: str, answer: str) -> dict:
        prompt = self._build_prompt(question, context, answer)

        raw = self.model.generate_response(
            user_text=prompt,
            language="english"
        )

        return self._parse_json_safely(raw)

    def _build_prompt(self, question: str, context: str, answer: str) -> str:
        return f"""
You are a strict factual-support verifier for a classroom robot.

Your job is NOT to answer the question.
Your job is only to decide whether the proposed answer is fully supported by the provided context.

Important rules:
- Use only the provided context.
- Do not use your own knowledge.
- Do not correct the answer.
- Do not rewrite the answer.
- Do not approve guesses.
- Do not approve claims that are not clearly supported by the context.
- If the context is missing the answer, reject.
- If the answer adds extra facts not found in the context, reject.
- If the answer changes numbers, dates, names, places, causes, or relationships, reject.
- If unsure, reject.

Approve only if every factual claim in the answer is clearly supported by the context.

Return only valid JSON.

JSON format:
{{
  "approved": true or false,
  "reason": "short reason",
  "unsupported_claims": ["claim 1", "claim 2"]
}}

Question:
{question}

Context:
{context}

Proposed answer:
{answer}
""".strip()

    def _parse_json_safely(self, raw_text: str) -> dict:
        try:
            # Extract first JSON object from the response
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)

            if not match:
                raise ValueError("No JSON object found.")

            data = json.loads(match.group(0))

            if "approved" not in data:
                raise ValueError("Missing approved field.")

            return {
                "approved": bool(data.get("approved", False)),
                "reason": str(data.get("reason", "")),
                "unsupported_claims": data.get("unsupported_claims", []),
            }

        except Exception:
            return {
                "approved": False,
                "reason": "Fact verifier returned invalid JSON.",
                "unsupported_claims": ["Unable to verify answer."],
            }