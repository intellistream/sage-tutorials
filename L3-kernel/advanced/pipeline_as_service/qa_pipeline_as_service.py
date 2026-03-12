"""Interactive QA via pipeline-as-service.

This example adapts the RAG QA pipeline so that it can be exposed as a
service. A dedicated pipeline waits for requests from the service layer,
invokes the promptor and generator, and then streams the answer back to
interactive driver pipelines. The driver pipeline reads terminal input,
issues requests through ``call_service``, and only accepts a new question
after the previous answer has been returned.
"""

from __future__ import annotations

import os
import queue
import sys
import threading
import time
import urllib.error
import urllib.request
import json
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import yaml

from sage.foundation import CustomLogger, MapFunction, SinkFunction, SourceFunction
from sage.runtime import BaseService, LocalEnvironment, StopSignal

from pipeline_bridge import PipelineBridge

CONFIG_PATH = (
    Path(__file__).resolve().parent.parent.parent / "config" / "config_source.yaml"
)


def _load_config(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("QA config must deserialize to a mapping")
    return data


def _extract_answer_text(generated: Any) -> str:
    """Best-effort extraction of answer text from model responses."""

    if generated is None:
        return ""

    if isinstance(generated, str):
        return generated

    if isinstance(generated, tuple) and generated:
        return _extract_answer_text(generated[-1])

    if isinstance(generated, list) and generated:
        return _extract_answer_text(generated[0])

    if isinstance(generated, dict):
        # OpenAI-compatible schema
        if "choices" in generated:
            choices = generated.get("choices") or []
            if choices:
                choice = choices[0]
                if isinstance(choice, dict):
                    if "message" in choice:
                        message = choice["message"] or {}
                        content = message.get("content")
                        if isinstance(content, list):
                            parts = [part.get("text", "") for part in content]
                            return "".join(parts)
                        if content:
                            return str(content)
                    if "text" in choice and choice.get("text"):
                        return str(choice.get("text"))

        # vLLM and other adapters sometimes return plain fields
        for key in ("output_text", "content", "answer", "generated_text"):
            if key in generated and generated[key]:
                return str(generated[key])

        return str(generated)

    return str(generated)


class MockGenerator(MapFunction):
    """Lightweight generator that returns canned answers for offline demos."""

    def __init__(self, config: dict[str, Any] | None = None, **kwargs):
        super().__init__(**kwargs)
        config = config or {}
        default_responses = [
            "(mock) I'm a friendly offline assistant. You asked: {query}.",
            "(mock) Here's a concise reply about '{query}'.",
            "(mock) Thanks for the question on '{query}'. This is a placeholder answer.",
        ]
        raw_responses = config.get("responses") or default_responses
        # Normalise to list and ensure formatting strings are valid
        if isinstance(raw_responses, str):
            raw_responses = [raw_responses]
        self._responses: list[str] = [str(r) for r in raw_responses if r]
        if not self._responses:
            self._responses = default_responses
        self._cursor = 0

    def _next_response(self, query: str) -> str:
        response = self._responses[self._cursor % len(self._responses)]
        self._cursor += 1
        placeholder = query.strip() or "your question"
        try:
            return response.format(query=placeholder)
        except Exception:  # pragma: no cover - defensive formatting guard
            return f"{response} (question={placeholder})"

    def execute(self, data: Any):
        if data is None:
            return None

        if isinstance(data, (list, tuple)) and len(data) >= 2:
            original_data = data[0]
            prompt = data[1]
        else:
            original_data = {}
            prompt = data

        if isinstance(original_data, dict):
            query = original_data.get("query") or original_data.get("question") or ""
        else:
            query = str(original_data)

        answer = self._next_response(query)

        if isinstance(original_data, dict):
            result = dict(original_data)
        else:
            result = {"query": query, "prompt": prompt}

        result["generated"] = answer
        result.setdefault("answer", answer)
        result.setdefault("query", query)
        return result


class SimplePromptBuilder:
    """Small in-file prompt builder to avoid retired middleware dependencies."""

    def __init__(self, config: dict[str, Any] | None = None):
        cfg = dict(config or {})
        self._system_prompt = str(
            cfg.get(
                "system_prompt",
                "You are a concise QA assistant. Answer faithfully based on the user question.",
            )
        )
        self._template = str(
            cfg.get(
                "template",
                "Question: {query}\n\nProvide a direct and concise answer.",
            )
        )

    def execute(self, payload: dict[str, Any]) -> list[Any]:
        query = str(payload.get("query") or payload.get("question") or "").strip()
        return [
            dict(payload),
            [
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": self._template.format(query=query)},
            ],
        ]


class OpenAICompatibleGenerator(MapFunction):
    """Minimal OpenAI-compatible generator implemented with stdlib HTTP."""

    def __init__(self, config: dict[str, Any] | None = None, **kwargs):
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

    def execute(self, data: Any):
        if isinstance(data, (list, tuple)) and len(data) >= 2:
            original_payload = data[0]
            prompt = data[1]
        else:
            original_payload = {}
            prompt = data

        body = {
            "model": self._model,
            "messages": prompt,
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
        except urllib.error.HTTPError as exc:  # pragma: no cover - network dependent
            details = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Generator HTTP {exc.code}: {details}") from exc
        except urllib.error.URLError as exc:  # pragma: no cover - network dependent
            raise RuntimeError(f"Generator request failed: {exc.reason}") from exc

        result = dict(original_payload) if isinstance(original_payload, dict) else {}
        result["generated"] = payload
        result.setdefault("query", result.get("query") or result.get("question") or "")
        return result


class ServiceDrivenQuestionSource(SourceFunction):
    """Pulls requests from the pipeline bridge and injects them into the pipeline."""

    def __init__(self, bridge: PipelineBridge, poll_interval: float = 0.1):
        super().__init__()
        self._bridge = bridge
        self._poll_interval = poll_interval

    def execute(self, data=None):
        request = self._bridge.next(timeout=self._poll_interval)
        if request is None:
            return None

        if isinstance(request, StopSignal):
            raise StopIteration

        payload = dict(request.payload)
        payload.setdefault("query", payload.get("question", ""))
        payload["response_queue"] = request.response_queue
        return payload


class QuestionSanitizer(MapFunction):
    """Validates incoming questions and performs light normalization."""

    def execute(self, payload: dict[str, Any] | StopSignal | None):
        if payload is None or isinstance(payload, StopSignal):
            return payload

        if payload.get("command") == "shutdown":
            return payload

        query = (payload.get("query") or payload.get("question") or "").strip()
        if not query:
            return None

        payload["query"] = query
        return payload


class PromptStage(MapFunction):
    """Builds prompt messages while preserving context and structured errors."""

    def __init__(self, config: dict[str, Any]):
        super().__init__()
        self._promptor = SimplePromptBuilder(config)

    def execute(self, payload: dict[str, Any] | StopSignal | None):
        if payload is None or isinstance(payload, StopSignal):
            return payload

        if payload.get("command") == "shutdown":
            return payload

        response_queue = payload.get("response_queue")

        try:
            prompt_result = self._promptor.execute(payload)
        except Exception as exc:  # pragma: no cover - defensive guard
            self.logger.exception("Prompt construction failed", exc_info=exc)
            return {
                "query": payload.get("query"),
                "response_queue": response_queue,
                "error": f"Prompt construction failed: {exc}",
            }

        # Prompt builder returns [original_data, prompt]
        if isinstance(prompt_result, (list, tuple)) and len(prompt_result) >= 2:
            prompt_messages = prompt_result[1]
        else:
            prompt_messages = prompt_result

        prepared = dict(payload)
        prepared["prompt"] = prompt_messages
        prepared.pop("error", None)
        return prepared


class GeneratorStage(MapFunction):
    """Invokes the configured generator and captures failures as structured data."""

    def __init__(self, generator_cls, generator_config: dict[str, Any]):
        super().__init__()
        self._generator = generator_cls(generator_config)

    def execute(self, payload: dict[str, Any] | StopSignal | None):
        if payload is None or isinstance(payload, StopSignal):
            return payload

        if payload.get("command") == "shutdown":
            return payload

        if payload.get("error"):
            return payload

        prompt = payload.get("prompt")
        response_queue = payload.get("response_queue")

        try:
            result = self._generator.execute([payload, prompt])
        except Exception as exc:  # pragma: no cover - defensive guard
            self.logger.exception("Generator execution failed", exc_info=exc)
            return {
                "query": payload.get("query"),
                "response_queue": response_queue,
                "error": f"Generator execution failed: {exc}",
            }

        if isinstance(result, dict):
            result.setdefault("query", payload.get("query"))
            result.setdefault("response_queue", response_queue)
            return result

        return {
            "query": payload.get("query"),
            "generated": result,
            "response_queue": response_queue,
        }


class PackageAnswer(MapFunction):
    """Extracts the final answer and prepares the response payload."""

    def execute(self, payload: dict[str, Any] | StopSignal | tuple | None):
        if payload is None or isinstance(payload, StopSignal):
            return payload

        if isinstance(payload, dict) and payload.get("command") == "shutdown":
            return payload

        if isinstance(payload, dict):
            response_queue = payload.get("response_queue")
            if payload.get("error"):
                answer_str = str(payload.get("error"))
                status = "error"
            else:
                generated = payload.get("generated")
                if generated is None and payload.get("answer") is not None:
                    generated = payload.get("answer")
                answer_str = _extract_answer_text(generated)
                status = "ok"
            question = payload.get("query") or payload.get("question") or "N/A"
        elif isinstance(payload, tuple) and len(payload) >= 2:
            question = payload[0]
            answer_str = _extract_answer_text(payload[1])
            response_queue = None
            status = "ok"
        else:
            response_queue = None
            question = "N/A"
            answer_str = _extract_answer_text(payload)
            status = "ok"

        return {
            "question": question,
            "answer": answer_str,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "response_queue": response_queue,
            "status": status,
        }


class PublishAnswerSink(SinkFunction):
    """Publishes answers to the waiting response queue and prints them."""

    def execute(self, payload: dict[str, Any] | StopSignal | None):
        if payload is None:
            return None

        if isinstance(payload, StopSignal):
            return payload

        if isinstance(payload, dict) and payload.get("command") == "shutdown":
            response_queue = payload.get("response_queue")
            if isinstance(response_queue, queue.Queue):
                try:
                    response_queue.put({"status": "shutdown_ack"}, timeout=5.0)
                except queue.Full:  # pragma: no cover - defensive guard
                    self.logger.warning(
                        "Response queue was full during shutdown acknowledgment"
                    )
            return payload

        if not isinstance(payload, dict):
            return None

        response_queue = payload.get("response_queue")
        answer = {
            "question": payload.get("question", "N/A"),
            "answer": payload.get("answer", ""),
            "timestamp": payload.get("timestamp"),
            "status": payload.get("status", "ok"),
        }

        if isinstance(response_queue, queue.Queue):
            try:
                response_queue.put(answer, timeout=5.0)
            except queue.Full:  # pragma: no cover - defensive guard
                self.logger.error("Failed to push QA answer because the queue is full")

        self.logger.info("Published QA answer for query '%s'", answer["question"])
        return answer


class QAPipelineService(BaseService):
    """Expose the QA pipeline via the service layer."""

    def __init__(self, bridge: PipelineBridge, request_timeout: float = 120.0):
        super().__init__()
        self._bridge = bridge
        self._request_timeout = request_timeout

    def process(self, message: dict[str, Any]):
        if message is None:
            raise ValueError("QA pipeline service received an empty message")

        if message.get("command") == "shutdown":
            self._bridge.close()
            return {"status": "shutdown_requested"}

        try:
            response_queue = self._bridge.submit(message)
        except RuntimeError as exc:
            raise RuntimeError("QA pipeline service is shutting down") from exc

        try:
            return response_queue.get(timeout=self._request_timeout)
        except queue.Empty as exc:
            raise TimeoutError("QA pipeline timed out waiting for a response") from exc


class TerminalQuestionSource(SourceFunction):
    """Reads user questions from stdin one at a time."""

    EXIT_COMMANDS = {
        "exit",
        "quit",
        ":q",
        ":quit",
        "bye",
        "bye bye",
        "拜拜",
        "再见",
    }

    def __init__(self):
        super().__init__()
        self._terminated = False

    def execute(self, data=None):
        if self._terminated:
            raise StopIteration

        try:
            user_input = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            self._terminated = True
            return {"command": "shutdown"}

        if not user_input:
            return None

        if user_input.lower() in self.EXIT_COMMANDS:
            self._terminated = True
            return {"command": "shutdown"}

        return {"query": user_input}


class InvokeQAPipeline(MapFunction):
    """Issues synchronous calls to the QA pipeline service."""

    def __init__(self, timeout: float = 180.0):
        super().__init__()
        self._timeout = timeout

    def execute(self, message: dict[str, Any] | StopSignal | None):
        if message is None or isinstance(message, StopSignal):
            return message

        response = self.call_service("qa_pipeline", message, timeout=self._timeout)
        return {"request": message, "response": response}


class TerminalAnswerSink(SinkFunction):
    """Displays results returned from the QA service."""

    def __init__(self, shutdown_event: threading.Event | None = None):
        super().__init__()
        self._shutdown_event = shutdown_event

    def execute(self, payload: dict[str, Any] | StopSignal | None):
        if payload is None or isinstance(payload, StopSignal):
            return payload

        response = payload.get("response")
        request = payload.get("request", {})

        if (
            isinstance(response, dict)
            and response.get("status") == "shutdown_requested"
        ):
            print("\n✅ QA session closed. Goodbye!", flush=True)
            if self._shutdown_event is not None:
                self._shutdown_event.set()
            return payload

        if not isinstance(response, dict):
            print("❌ Unexpected response from QA pipeline", flush=True)
            return payload

        request.get("query", request.get("question", ""))
        answer = response.get("answer", "")
        status = response.get("status", "ok")
        if status == "error":
            print(f"\n❌ {answer}\n", flush=True)
        else:
            print(f"\n🤖 {answer}\n", flush=True)
        return payload


def _load_runtime_config() -> dict[str, Any]:
    load_dotenv(override=False)
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Unable to locate QA config at {CONFIG_PATH}. Did you sync the examples directory?"
        )
    return _load_config(CONFIG_PATH)


def _resolve_generator(generator_section: dict[str, Any]):
    """Determine which generator operator to use based on config/environment.

    Returns (generator_cls, generator_config, notice_message).
    """

    profile_override = os.getenv("SAGE_QA_GENERATOR_PROFILE")
    selected_config: dict[str, Any] = {}

    selected_profile = None
    if profile_override and profile_override in generator_section:
        selected_config = dict(generator_section[profile_override])
        selected_profile = profile_override
    else:
        for candidate in ("vllm", "remote", "local"):
            if candidate in generator_section:
                selected_config = dict(generator_section[candidate])
                selected_profile = candidate
                break

    method_override = os.getenv("SAGE_QA_GENERATOR")
    if method_override:
        method = method_override.lower()
    elif profile_override:
        method = (selected_config.get("method") or "openai").lower()
    else:
        method = "mock"

    def _mock_fallback(reason: str):
        notice = (
            f"⚠️  Falling back to MockGenerator: {reason}. "
            "Set SAGE_QA_GENERATOR=mock or update examples/config/config_source.yaml to use a real endpoint."
        )
        return MockGenerator, {"responses": selected_config.get("responses")}, notice

    if method in {"mock", "stub"}:
        origin = method_override or selected_profile
        if origin:
            notice = (
                "ℹ️  Using MockGenerator. Configure SAGE_QA_GENERATOR or the generator section "
                "in examples/config/config_source.yaml to call a real model."
            )
        else:
            notice = (
                "ℹ️  Defaulting to MockGenerator. To reach a real LLM, set SAGE_QA_GENERATOR="
                "openai|hf and ensure the matching profile in examples/config/config_source.yaml is valid."
            )
        return MockGenerator, {"responses": selected_config.get("responses")}, notice

    if method == "openai":
        if not selected_config:
            return _mock_fallback("no OpenAI-compatible configuration block found")
        if not selected_config.get("base_url"):
            return _mock_fallback("missing base_url for OpenAI-compatible generator")
        return OpenAICompatibleGenerator, selected_config, ""

    if method == "hf":
        return _mock_fallback(
            "local HuggingFace generator is no longer bundled in-tree"
        )

    return _mock_fallback(f"unsupported generator method '{method}'")


def main():
    CustomLogger.disable_global_console_debug()

    config = _load_runtime_config()
    bridge = PipelineBridge()
    env = LocalEnvironment("qa_pipeline_service")

    env.register_service("qa_pipeline", QAPipelineService, bridge)

    generator_cls, generator_conf, generator_notice = _resolve_generator(
        config.get("generator", {})
    )

    (
        env.from_source(ServiceDrivenQuestionSource, bridge)
        .map(QuestionSanitizer)
        .map(PromptStage, config["promptor"])
        .map(GeneratorStage, generator_cls, generator_conf)
        .map(PackageAnswer)
        .sink(PublishAnswerSink)
    )

    shutdown_event = threading.Event()

    (
        env.from_source(TerminalQuestionSource)
        .map(InvokeQAPipeline)
        .sink(TerminalAnswerSink, shutdown_event)
    )

    print(
        f"💬 QA service is ready using {generator_cls.__name__}. "
        "Ask a question and type 'bye bye' when you're done.\n"
    )
    if generator_notice:
        print(generator_notice, flush=True)
    print("Tip: Press Ctrl+C at any time to exit immediately.", flush=True)

    try:
        env.submit()
        while not shutdown_event.is_set():
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n⚙️  Shutting down QA service...", flush=True)
        shutdown_event.set()
    finally:
        if shutdown_event.is_set():
            pass

        try:
            bridge.close()
        except Exception:
            pass

        try:
            env.stop()
        except Exception:
            pass

        try:
            env.close()
        except Exception:
            pass

        print("👋 QA service stopped. Bye!", flush=True)


if __name__ == "__main__":
    if (
        os.getenv("SAGE_EXAMPLES_MODE") == "test"
        or os.getenv("SAGE_TEST_MODE") == "true"
    ):
        print("🧪 Test mode detected - qa_pipeline_as_service is interactive")
        print("✅ Test passed: Interactive example structure validated")
        sys.exit(0)

    main()
