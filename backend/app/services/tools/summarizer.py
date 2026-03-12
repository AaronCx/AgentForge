import os

from langchain.tools import tool
from openai import AsyncOpenAI

from app.config import DEFAULT_MODEL


@tool
async def summarizer(text: str) -> str:
    """Summarize long text into a concise, well-structured summary. Preserves key information and action items."""
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

    response = await client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert summarizer. Create a clear, well-structured summary of the given text. "
                    "Include: 1) A brief overview (2-3 sentences), 2) Key points as bullet points, "
                    "3) Action items if any, 4) Important dates/deadlines if mentioned."
                ),
            },
            {"role": "user", "content": text[:8000]},
        ],
        temperature=0,
    )

    return response.choices[0].message.content or "Unable to generate summary."
