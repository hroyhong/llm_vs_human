import os
from openai import OpenAI
from dotenv import load_dotenv

def test_api_connection():
    """Loads API key and makes a simple test call to OpenRouter."""
    load_dotenv()  # Load variables from .env file
    api_key = os.getenv("LLM_API_KEY")

    if not api_key:
        print("Error: LLM_API_KEY not found in .env file.")
        return False

    print("API Key loaded successfully.")

    # Configure the OpenAI client to use OpenRouter
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    try:
        print("Attempting to connect to OpenRouter...")
        # Use a cheap and fast model for testing
        completion = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free", # Or another fast model like nousresearch/nous-hermes-2-mistral-7b-dpo
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
            max_tokens=10,
            temperature=0.1,
        )
        print("API Call Successful!")
        print("Response:", completion.choices[0].message.content)
        return True
    except Exception as e:
        print(f"Error connecting to OpenRouter API: {e}")
        return False

if __name__ == "__main__":
    test_api_connection() 