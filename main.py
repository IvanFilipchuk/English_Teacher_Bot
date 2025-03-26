# # from huggingface_hub import InferenceClient
# #
# # MODEL_NAME = "tiiuae/falcon-7b-instruct"
# # API_TOKEN = "###########################"
# #
# # client = InferenceClient(model=MODEL_NAME, token=API_TOKEN)
# #
# # def test_model():
# #     prompt = "Correct this sentence: 'He go to school.' Return only the corrected version."
# #
# #     response = client.text_generation(
# #         prompt,
# #         max_new_tokens=50,
# #         temperature=0.5,
# #         stream=False
# #     )
# #
# #     print("Odpowiedź AI:", response.strip())
# #
# # if __name__ == "__main__":
# #     test_model()


import logging
from telegram.ext import Application
from config.config import Config
from bot.handlers import base, dictionary

def main():
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

    base.BaseHandlers.register_handlers(application)
    dictionary.DictionaryHandlers.register_handlers(application)

    logging.info("✅ Bot starting polling ...")
    application.run_polling()

if __name__ == "__main__":
    main()