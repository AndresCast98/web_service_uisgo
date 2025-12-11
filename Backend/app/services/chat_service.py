from __future__ import annotations

from typing import List, Dict

import httpx
from openai import OpenAI

from app.core.config import settings
from app.services.chat_policy import DEFAULT_POLICY

_client: OpenAI | None = None
_httpx_client: httpx.Client | None = None


def get_client() -> OpenAI:
    global _client, _httpx_client
    if _client is None:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        _httpx_client = httpx.Client(timeout=30)
        _client = OpenAI(api_key=settings.OPENAI_API_KEY, http_client=_httpx_client)
    return _client


def generate_ai_reply(history: List[Dict[str, str]]) -> str:
    messages = [
        {"role": "system", "content": DEFAULT_POLICY.system_prompt}
    ] + history
    client = get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.6,
    )
    return response.choices[0].message.content or ""
