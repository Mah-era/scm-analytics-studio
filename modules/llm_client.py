"""Optional LLM integration for workflow routing and narrative summaries.

The app works without this module making any network calls. LLM calls only run
when the user explicitly enables them and provides an API key.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMConfig:
    enabled: bool = False
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1/chat/completions"


def config_from_env() -> LLMConfig:
    api_key = os.getenv("OPENAI_API_KEY", "")
    enabled = os.getenv("SCM_ENABLE_LLM", "").lower() in {"1", "true", "yes"} and bool(api_key)
    return LLMConfig(
        enabled=enabled,
        model=os.getenv("SCM_LLM_MODEL", "gpt-4o-mini"),
        api_key=api_key,
        base_url=os.getenv("SCM_LLM_BASE_URL", "https://api.openai.com/v1/chat/completions"),
    )


def summarize_with_llm(prompt: str, config: LLMConfig | None = None) -> str:
    cfg = config or config_from_env()
    if not cfg.enabled:
        return "LLM integration is disabled. Enable SCM_ENABLE_LLM=1 and provide OPENAI_API_KEY to use it."

    payload = {
        "model": cfg.model,
        "messages": [
            {
                "role": "system",
                "content": "You summarize offline SCM analytics results clearly and concisely. Do not claim access to data not provided.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    request = urllib.request.Request(
        cfg.base_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {cfg.api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]
    except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError) as exc:
        return f"LLM request failed: {exc}"
