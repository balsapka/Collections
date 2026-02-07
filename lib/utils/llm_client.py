"""
Shared LLM client wrapper for all agents.
Reads ANTHROPIC_API_KEY from environment. Model defaults to claude-sonnet-4-5-20250514
but can be overridden via CLAUDE_MODEL env var or per-call.
"""

import os
from anthropic import Anthropic

DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250514")
_client = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY not set. Export it or add to .env file."
            )
        _client = Anthropic(api_key=api_key)
    return _client


def call_llm(
    system_prompt: str,
    user_content: str,
    model: str | None = None,
    max_tokens: int = 8192,
    temperature: float = 0.2,
) -> str:
    """Single-turn LLM call. Returns the assistant text response."""
    client = get_client()
    response = client.messages.create(
        model=model or DEFAULT_MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return response.content[0].text
