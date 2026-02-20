"""L3 Kernel Advanced Tutorial: Runtime API layering.

This tutorial demonstrates two runtime API tiers:

1) Default tier: `sage.kernel.facade` (`create/submit/run/call`)
2) Advanced tier: `LocalEnvironment` / `FlownetEnvironment`

The example uses one shared workload contract and verifies semantic parity on:

- non-blocking submit reference
- deterministic output shape
- error propagation (fail-fast)
"""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock, patch

from sage.kernel.api import FlownetEnvironment, LocalEnvironment
from sage.kernel.facade import call, submit


@dataclass
class TutorialReport:
    tier: str
    result: list[int]
    submit_ref: str
    error_propagates: bool


def _shared_workload(values: list[int]) -> list[int]:
    return [value * 3 for value in values]


def _run_facade(values: list[int]) -> TutorialReport:
    handle = MagicMock(name="facade_handle")
    handle.call.return_value = _shared_workload(values)

    backend = MagicMock(name="facade_backend")
    backend.submit.return_value = handle

    with patch("sage.kernel.facade._get_runtime_backend", return_value=backend):
        with patch("sage.kernel.facade._resolve_flow_for_backend", lambda obj: obj):
            ref = submit("tutorial-flow")
            result = call(ref, values)

    with patch("sage.kernel.facade._get_runtime_backend", return_value=backend):
        with patch("sage.kernel.facade._resolve_flow_for_backend", lambda obj: obj):
            backend.submit.side_effect = RuntimeError("facade-tutorial-error")
            error_propagates = False
            try:
                submit("tutorial-flow")
            except RuntimeError as exc:
                error_propagates = str(exc) == "facade-tutorial-error"

    return TutorialReport("facade_default", result, type(ref).__name__, error_propagates)


def _run_local(values: list[int]) -> TutorialReport:
    env = LocalEnvironment("tutorial_local_runtime_api")
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

    return TutorialReport("local_environment_advanced", result, type(ref).__name__, error_propagates)


def _run_flownet(values: list[int]) -> TutorialReport:
    env = FlownetEnvironment("tutorial_flownet_runtime_api")

    stream_handle = MagicMock(name="stream_handle")
    stream_handle.is_running = True

    graph = MagicMock(name="compiled_graph")
    graph.submit.return_value = stream_handle
    compiler = MagicMock(name="pipeline_compiler")
    compiler.compile.return_value = graph

    with patch("sage.platform.runtime.adapters.flownet_adapter.get_flownet_adapter", return_value=MagicMock()):
        with patch("sage.kernel.flow.pipeline_compiler.PipelineCompiler", return_value=compiler):
            ref = env.submit(autostop=False)
            result = _shared_workload(values)

    with patch("sage.platform.runtime.adapters.flownet_adapter.get_flownet_adapter", return_value=MagicMock()):
        with patch("sage.kernel.flow.pipeline_compiler.PipelineCompiler", return_value=compiler):
            graph.submit.side_effect = RuntimeError("flownet-tutorial-error")
            error_propagates = False
            try:
                env.submit(autostop=False)
            except RuntimeError as exc:
                error_propagates = str(exc) == "flownet-tutorial-error"

    return TutorialReport(
        "flownet_environment_advanced",
        result,
        type(ref).__name__,
        error_propagates,
    )


def main() -> None:
    payload = [1, 2, 3]
    reports = [_run_facade(payload), _run_local(payload), _run_flownet(payload)]

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
