import openai
import json
import logging
from typing import Optional
from config.config import Config
from datetime import datetime

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.MODEL_NAME
        self.max_tokens = 150
        self.temperature = 0.3
        logger.info("AI Service initialized with model: %s", self.model)

    async def check_sentence(self, word: str, sentence: str) -> dict:
        try:
            start_time = datetime.now()
            response = await self._get_ai_correction(word, sentence)
            result = self._parse_response(response, sentence)

            logger.info(
                "AI correction took %.2fs | Word: %s",
                (datetime.now() - start_time).total_seconds(),
                word
            )
            return result
        except Exception as e:
            logger.error("AI correction failed: %s", str(e))
            return {
                "is_correct": False,
                "correction": sentence,
                "feedback": f"Error: {str(e)}"
            }

    async def _get_ai_correction(self, word: str, sentence: str) -> str:
        messages = [{
            "role": "system",
            "content": "You are an English teacher. Correct sentences concisely."
        }, {
            "role": "user",
            "content": f"Correct this using '{word}': '{sentence}'. Return JSON with: is_correct, correction, explanation"
        }]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content

    def _parse_response(self, response: str, original: str) -> dict:
        try:
            data = json.loads(response)
            return {
                "is_correct": data.get("is_correct", False),
                "correction": data.get("correction", original),
                "feedback": data.get("explanation", "No feedback")
            }
        except json.JSONDecodeError:
            return {
                "is_correct": False,
                "correction": original,
                "feedback": "Invalid response format"
            }