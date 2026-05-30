"""LLM provider factory.

KubeSentient supports two chat backends and selects between them at runtime via
the ``LLM_PROVIDER`` environment variable. OpenAI remains the default so any
existing deployment keeps the same behaviour. Setting ``LLM_PROVIDER=anthropic``
switches the agent over to Claude without touching the LangGraph wiring.

The factory raises early with an actionable error message when a required
package or API key is missing, so misconfigurations show up at startup instead
of inside the first tool call.
"""

from __future__ import annotations

import os
from typing import Literal

Provider = Literal["openai", "anthropic"]

_DEFAULT_OPENAI_MODEL = "gpt-4-turbo-preview"
_DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"


def _resolve_provider() -> Provider:
    raw = os.getenv("LLM_PROVIDER", "openai").strip().lower()
    if raw in ("openai", "anthropic"):
        return raw  # type: ignore[return-value]
    raise ValueError(
        f"Unsupported LLM_PROVIDER={raw!r}. Expected 'openai' or 'anthropic'."
    )


def _build_openai(temperature: float):
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise ImportError(
            "LLM_PROVIDER=openai requires the 'langchain-openai' package. "
            "Install it with: pip install langchain-openai"
        ) from exc

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "LLM_PROVIDER=openai but OPENAI_API_KEY is not set. "
            "Either export the key or switch to LLM_PROVIDER=anthropic."
        )

    model = os.getenv("OPENAI_MODEL", _DEFAULT_OPENAI_MODEL)
    return ChatOpenAI(model=model, temperature=temperature)


def _build_anthropic(temperature: float):
    try:
        from langchain_anthropic import ChatAnthropic
    except ImportError as exc:
        raise ImportError(
            "LLM_PROVIDER=anthropic requires the 'langchain-anthropic' package. "
            "Install it with: pip install langchain-anthropic"
        ) from exc

    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is not set. "
            "Get one at https://console.anthropic.com/ and export it."
        )

    model = os.getenv("ANTHROPIC_MODEL", _DEFAULT_ANTHROPIC_MODEL)
    return ChatAnthropic(model=model, temperature=temperature)


def build_llm(temperature: float = 0.0):
    """Return a configured LangChain chat model for the active provider.

    The agent always uses ``temperature=0`` for deterministic investigations.
    Callers that need a different value (e.g. for creative summarisation) can
    pass it explicitly.
    """
    provider = _resolve_provider()
    if provider == "anthropic":
        return _build_anthropic(temperature)
    return _build_openai(temperature)
