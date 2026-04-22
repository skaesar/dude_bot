from openai import AsyncOpenAI
from config import config

client = AsyncOpenAI(
    api_key=config.openrouter_api_key,
    base_url="https://openrouter.ai/api/v1"
)

async def ask_gemma(history: list, user_message: str) -> str:
    messages = history + [{"role": "user", "content": user_message}]

    response = await client.chat.completions.create(
        model=config.model,
        messages=messages
    )
    return response.choices[0].message.content