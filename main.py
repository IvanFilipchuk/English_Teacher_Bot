from huggingface_hub import InferenceClient

MODEL_NAME = "tiiuae/falcon-7b-instruct"
API_TOKEN = "###########################"

client = InferenceClient(model=MODEL_NAME, token=API_TOKEN)

def test_model():
    prompt = "Correct this sentence: 'He go to school.' Return only the corrected version."

    response = client.text_generation(
        prompt,
        max_new_tokens=50,
        temperature=0.5,
        stream=False
    )

    print("Odpowiedź AI:", response.strip())

if __name__ == "__main__":
    test_model()
