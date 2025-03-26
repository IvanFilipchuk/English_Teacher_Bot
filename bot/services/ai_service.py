from huggingface_hub import InferenceClient
from config.config import Config
import re

class AIService:
    def __init__(self):
        self.client = InferenceClient(
            model=Config.MODEL_NAME,
            token=Config.HF_API_TOKEN
        )

    async def check_sentence(self, word: str, sentence: str) -> dict:
        try:
            prompt = (
                f"Correct this sentence using the word '{word}': '{sentence}'. "
                f"Return only the corrected version or the original if already correct."
            )

            response = self.client.text_generation(
                prompt,
                max_new_tokens=50,
                temperature=0.5,
                stream=False
            ).strip()

            corrected = re.sub(r'^"|"$', '', response.strip())
            is_correct = corrected.lower() == sentence.lower()

            return {
                "is_correct": is_correct,
                "feedback": "The sentence is correct" if is_correct
                          else f"Suggested correction: {corrected}",
                "correction": corrected if not is_correct else ""
            }
        except Exception as e:
            return {
                "error": str(e),
                "is_correct": False,
                "feedback": "Could not analyze your sentence due to an error"
            }