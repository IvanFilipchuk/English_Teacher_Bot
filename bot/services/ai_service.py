import json

from huggingface_hub import InferenceClient
from config.config import Config
import re

class AIService:
    def __init__(self):
        try:
            self.client = InferenceClient(
                model=Config.MODEL_NAME,
                token=Config.HF_API_TOKEN
            )
        except Exception as e:
            print(f"Failed to initialize AI client: {str(e)}")
            self.client = None

    async def check_sentence(self, word: str, sentence: str) -> dict:
        if not self.client:
            return {
                "is_correct": False,
                "feedback": "AI service is currently unavailable",
                "correction": sentence,
                "error": "AI service offline"
            }

        try:
            prompt = (
                f"Correct this English sentence using the word '{word}': '{sentence}'.\n"
                "Provide response in JSON format with these fields:\n"
                "- is_correct (boolean)\n"
                "- correction (string)\n"
                "- explanation (string)\n\n"
                "Example response:\n"
                '{"is_correct": false, "correction": "She likes running", "explanation": "Use third person singular form"}'
            )

            response = self.client.text_generation(
                prompt,
                max_new_tokens=200,
                temperature=0.3
            ).strip()

            # Parse the response (add error handling)
            try:
                if response.startswith('{') and response.endswith('}'):
                    result = json.loads(response)
                else:
                    # Fallback for malformed response
                    result = {
                        "is_correct": False,
                        "correction": sentence,
                        "explanation": "Could not parse AI response"
                    }
            except json.JSONDecodeError:
                result = {
                    "is_correct": False,
                    "correction": sentence,
                    "explanation": "AI returned invalid response"
                }

            return {
                "is_correct": result.get("is_correct", False),
                "feedback": result.get("explanation", "No feedback provided"),
                "correction": result.get("correction", sentence)
            }

        except Exception as e:
            return {
                "is_correct": False,
                "feedback": f"AI error: {str(e)}",
                "correction": sentence,
                "error": str(e)
            }