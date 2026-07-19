import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenRouter API Configuration
_env_key = os.getenv("OPENROUTER_API_KEY", "")
API_KEYS = [_env_key.strip()] if _env_key.strip() else []

if not API_KEYS:
    print("Warning: OPENROUTER_API_KEY not found in .env")

BASE_URL = "https://openrouter.ai/api/v1"

MODEL_MAP = {
    "qwen": "qwen/qwen-2.5-72b-instruct",
    "openai": "openai/gpt-4o-mini",
    "kimi": "meta-llama/llama-3.1-8b-instruct",
    "minimax": "mistralai/mistral-7b-instruct",
}
current_key_index = 0

def get_next_key():
    global current_key_index

    if not API_KEYS or API_KEYS == [""]:
        raise ValueError("❌ No API keys found. Set NVIDIA_API_KEYS env variable.")

    key = API_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    return key
def call_model_with_keys(prompt, model="qwen"):
    errors = []

    for _ in range(len(API_KEYS)):
        try:
            client = OpenAI(
                api_key=get_next_key(),
                base_url=BASE_URL,
                timeout=20
            )

            response = client.chat.completions.create(
                model=MODEL_MAP.get(model, MODEL_MAP["qwen"]),
                messages=[
                    {"role": "system", "content": "You are a professional financial AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=800
            )

            return response.choices[0].message.content

        except Exception as e:
            errors.append(str(e))
            continue

    return f"❌ All API keys failed.\n\nErrors:\n" + "\n".join(errors[:3])
def enhance_response(user_query, analysis_text):
    try:
        client = OpenAI(
            api_key=get_next_key(),
            base_url=BASE_URL,
            timeout=15
        )

        prompt = f"""
User Question:
{user_query}

Stock Analysis:
{analysis_text}

Task:
Explain clearly like a smart financial advisor.
- Keep it simple
- Give final recommendation
- Mention risks
"""

        res = client.chat.completions.create(
            model=MODEL_MAP["qwen"],
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=500
        )

        return res.choices[0].message.content

    except Exception:
        return analysis_text