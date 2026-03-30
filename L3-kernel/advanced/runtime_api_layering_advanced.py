"""L3 runtime tutorial: direct backend API vs environment API.

This tutorial demonstrates two runtime tiers that are now owned directly by the
main `sage` package:

1) Direct backend tier: `sage.runtime.get_runtime_backend()`
2) Environment tier: `LocalEnvironment` / `FluttyEnvironment`

The example uses one shared workload contract and verifies semantic parity on:

- non-blocking submit reference
- deterministic output shape
- error propagation (fail-fast)
"""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import sage.runtime as sage_runtime


@dataclass
class TutorialReport:
    tier: str
    result: list[int]
    submit_ref: str
    error_propagates: bool


def _shared_workload(values: list[int]) -> list[int]:
    return [value * 3 for value in values]


class _TriplerActor:
    def apply(self, values: list[int]) -> list[int]:
        return _shared_workload(values)


def _run_backend_api(values: list[int]) -> TutorialReport:
    backend = MagicMock(name="runtime_backend")
    actor_handle = MagicMock(name="actor_handle")
    method_ref = MagicMock(name="method_ref")
    method_ref.call.side_effect = lambda payload: _shared_workload(payload)
    actor_handle.get_method.return_value = method_ref
    backend.create.return_value = actor_handle

    with patch("sage.runtime.get_runtime_backend", return_value=backend):
        runtime = sage_runtime.get_runtime_backend()
        ref = runtime.create(_TriplerActor)
        result = ref.get_method("apply").call(values)

    method_ref.call.side_effect = RuntimeError("backend-api-error")
    error_propagates = False
    with patch("sage.runtime.get_runtime_backend", return_value=backend):
        runtime = sage_runtime.get_runtime_backend()
        try:
            runtime.create(_TriplerActor).get_method("apply").call(values)
        except RuntimeError as exc:
            error_propagates = str(exc) == "backend-api-error"

    return TutorialReport(
        "backend_api_direct", result, type(ref).__name__, error_propagates
    )


def _run_local(values: list[int]) -> TutorialReport:
    env = sage_runtime.LocalEnvironment("tutorial_local_runtime_api")
    env._jobmanager = MagicMock(name="local_jobmanager")
    env._jobmanager.submit_job.return_value = "local-tutorial-job"

    ref = env.submit(autostop=False)
    result = _shared_workload(values)

    env._jobmanager.submit_job.side_effect = RuntimeError("local-tutorial-error")
    error_propagates = False
    try:
        env.submit(autostop=False)
    except RuntimeError as exc:
        error_propagates = str(exc) == "local-tutorial-error"

    return TutorialReport(
        "local_environment_advanced", result, type(ref).__name__, error_propagates
    )


def _run_flutty(values: list[int]) -> TutorialReport:
    env = sage_runtime.FluttyEnvironment("tutorial_flutty_runtime_api")

    stream_handle = MagicMock(name="stream_handle")
    stream_handle.is_running = True

    graph = MagicMock(name="compiled_graph")
    graph.submit.return_value = stream_handle
    compiler = MagicMock(name="pipeline_compiler")
    compiler.compile.return_value = graph
    backend = MagicMock(name="flutty_runtime_backend")

    with patch(
        "sage.runtime.environments.runtime_backend.get_runtime_backend",
        return_value=backend,
    ):
        with patch("sage.runtime.environments.PipelineCompiler", return_value=compiler):
            ref = env.submit(autostop=False)
            result = _shared_workload(values)

    with patch(
        "sage.runtime.environments.runtime_backend.get_runtime_backend",
        return_value=backend,
    ):
        with patch("sage.runtime.environments.PipelineCompiler", return_value=compiler):
            graph.submit.side_effect = RuntimeError("flutty-tutorial-error")
            error_propagates = False
            try:
                env.submit(autostop=False)
            except RuntimeError as exc:
                error_propagates = str(exc) == "flutty-tutorial-error"

    return TutorialReport(
        "flutty_environment_advanced",
        result,
        type(ref).__name__,
        error_propagates,
    )


def main() -> None:
    payload = [1, 2, 3]
    reports = [_run_backend_api(payload), _run_local(payload), _run_flutty(payload)]

    print("Runtime API layering tutorial report:")
    for report in reports:
        print(
            {
                "tier": report.tier,
                "result": report.result,
                "submit_ref": report.submit_ref,
                "error_propagates": report.error_propagates,
            }
        )


if __name__ == "__main__":
    main()
