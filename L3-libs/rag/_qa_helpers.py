"""Small helpers for consolidated QA tutorials."""

from __future__ import annotations

import json
import os
import typing
import urllib

import yaml
from sage.foundation import MapFunction


def load_config(path: str) -> dict[str, typing.Any]:
    with open(path, encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config must be a mapping: {path}")
    return data


class SimplePromptor(MapFunction):
    """Build a minimal chat prompt from a query string."""

    def __init__(self, config: dict[str, typing.Any] | None = None, **kwargs):
        super().__init__(**kwargs)
        cfg = dict(config or {})
        self._system_prompt = str(
            cfg.get(
                "system_prompt",
                "You are a concise QA assistant. Answer directly and faithfully.",
            )
        )
        self._template = str(
            cfg.get(
                "template",
                "Question: {query}\n\nProvide a direct and concise answer.",
            )
        )

    def execute(self, data: typing.Any):
        query = str(data).strip()
        return [
            query,
            [
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": self._template.format(query=query)},
            ],
        ]


class OpenAICompatibleGenerator(MapFunction):
    """Minimal generator for OpenAI-compatible endpoints."""

    def __init__(self, config: dict[str, typing.Any] | None = None, **kwargs):
        super().__init__(**kwargs)
        cfg = dict(config or {})
        self._base_url = str(
            cfg.get("base_url")
            or os.getenv("SAGE_CHAT_BASE_URL")
            or os.getenv("OPENAI_BASE_URL")
            or ""
        ).rstrip("/")
        self._api_key = str(
            cfg.get("api_key")
            or os.getenv("SAGE_CHAT_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or ""
        )
        self._model = str(
            cfg.get("model")
            or cfg.get("model_name")
            or os.getenv("SAGE_CHAT_MODEL")
            or os.getenv("SAGELLM_MODEL_NAME")
            or "gpt-4o-mini"
        )
        self._temperature = float(cfg.get("temperature", 0.2))
        self._max_tokens = int(cfg.get("max_tokens", 256))
        if not self._base_url:
            raise ValueError("OpenAICompatibleGenerator requires base_url")

    def execute(self, data: typing.Any):
        if not isinstance(data, (list, tuple)) or len(data) < 2:
            raise ValueError("Generator expects [query, messages]")

        query = str(data[0])
        messages = data[1]
        body = {
            "model": self._model,
            "messages": messages,
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
            "stream": False,
        }
        request = urllib.request.Request(
            f"{self._base_url}/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                **(
                    {"Authorization": f"Bearer {self._api_key}"}
                    if self._api_key
                    else {}
                ),
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:  # pragma: no cover
            details = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Generator HTTP {exc.code}: {details}") from exc
        except urllib.error.URLError as exc:  # pragma: no cover
            raise RuntimeError(f"Generator request failed: {exc.reason}") from exc

        content = payload["choices"][0]["message"]["content"]
        return query, content
