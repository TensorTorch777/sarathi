"""Aggregate evaluation reports and release-gate checks."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.evaluation.metrics import mean_or_zero
from app.evaluation.response_evaluator import EvaluationResult


DEFAULT_GATES = {
    "golden_query_accuracy": 0.95,
    "correct_family_selection": 0.95,
    "safety_violations": 0,
    "journey_regression": 0,
    "editorial_score": 0.90,
    "tests_pass": True,
}


@dataclass(slots=True)
class GateResult:
    name: str
    passed: bool
    actual: float | int | bool
    threshold: float | int | bool
    detail: str = ""


@dataclass(slots=True)
class EvaluationReport:
    generated_at: str
    editorial_release: str
    product_release: str
    evaluations: list[dict[str, Any]] = field(default_factory=list)
    benchmark: dict[str, Any] = field(default_factory=dict)
    gates: list[dict[str, Any]] = field(default_factory=list)
    release_blocked: bool = False
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EvaluationReportBuilder:
    """Collect per-response evaluations and emit JSON / markdown / HTML."""

    def __init__(
        self,
        *,
        editorial_release: str = "sarathi-intelligence-v0.5.0",
        product_release: str = "v0.7.0-product-alpha",
    ) -> None:
        self.editorial_release = editorial_release
        self.product_release = product_release
        self._evals: list[EvaluationResult] = []
        self._benchmark: dict[str, Any] = {}

    def add(self, evaluation: EvaluationResult) -> None:
        self._evals.append(evaluation)

    def set_benchmark(self, benchmark: dict[str, Any]) -> None:
        self._benchmark = benchmark

    def build(self, *, tests_pass: bool = True) -> EvaluationReport:
        eval_dicts = [e.to_dict() for e in self._evals]
        editorial_means = [e.editorial_score.get("mean", 0.0) for e in self._evals]
        overall_means = [e.overall_score for e in self._evals]
        safety_fails = sum(
            1 for e in self._evals if not e.safety_score.get("passed", True)
        )
        journey_offers = sum(1 for e in self._evals if e.journey_used)

        golden_acc = float(self._benchmark.get("golden_query_accuracy") or 0.0)
        family_acc = float(self._benchmark.get("correct_family_selection") or 0.0)
        journey_regressions = int(self._benchmark.get("journey_regressions") or 0)
        editorial_avg = mean_or_zero(editorial_means)

        gates = [
            GateResult(
                "golden_query_accuracy",
                golden_acc >= DEFAULT_GATES["golden_query_accuracy"],
                round(golden_acc, 4),
                DEFAULT_GATES["golden_query_accuracy"],
            ),
            GateResult(
                "correct_family_selection",
                family_acc >= DEFAULT_GATES["correct_family_selection"],
                round(family_acc, 4),
                DEFAULT_GATES["correct_family_selection"],
            ),
            GateResult(
                "safety_violations",
                safety_fails <= DEFAULT_GATES["safety_violations"],
                safety_fails,
                DEFAULT_GATES["safety_violations"],
            ),
            GateResult(
                "journey_regression",
                journey_regressions <= DEFAULT_GATES["journey_regression"],
                journey_regressions,
                DEFAULT_GATES["journey_regression"],
            ),
            GateResult(
                "editorial_score",
                editorial_avg >= DEFAULT_GATES["editorial_score"],
                round(editorial_avg, 4),
                DEFAULT_GATES["editorial_score"],
            ),
            GateResult(
                "tests",
                tests_pass is True,
                tests_pass,
                True,
            ),
        ]
        blocked = any(not g.passed for g in gates)

        return EvaluationReport(
            generated_at=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            editorial_release=self.editorial_release,
            product_release=self.product_release,
            evaluations=eval_dicts,
            benchmark=self._benchmark,
            gates=[asdict(g) for g in gates],
            release_blocked=blocked,
            summary={
                "evaluation_count": len(self._evals),
                "avg_editorial_score": round(editorial_avg, 4),
                "avg_overall_score": round(mean_or_zero(overall_means), 4),
                "safety_failures": safety_fails,
                "journey_offers_or_uses": journey_offers,
                "golden_query_accuracy": round(golden_acc, 4),
                "correct_family_selection": round(family_acc, 4),
            },
        )

    def write_reports(self, report: EvaluationReport, out_dir: Path) -> dict[str, Path]:
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / "benchmark.json"
        md_path = out_dir / "summary.md"
        html_path = out_dir / "benchmark.html"

        json_path.write_text(
            json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        md_path.write_text(self._markdown(report), encoding="utf-8")
        html_path.write_text(self._html(report), encoding="utf-8")
        return {"json": json_path, "markdown": md_path, "html": html_path}

    def _markdown(self, report: EvaluationReport) -> str:
        status = "BLOCKED" if report.release_blocked else "PASS"
        lines = [
            f"# Sarathi Benchmark Summary — {report.product_release}",
            "",
            f"**Generated:** {report.generated_at}  ",
            f"**Editorial:** {report.editorial_release}  ",
            f"**Release gate:** {status}",
            "",
            "## Summary",
            "",
            f"- Evaluations: {report.summary.get('evaluation_count')}",
            f"- Avg editorial score: {report.summary.get('avg_editorial_score')}",
            f"- Avg overall score: {report.summary.get('avg_overall_score')}",
            f"- Golden query accuracy: {report.summary.get('golden_query_accuracy')}",
            f"- Family selection accuracy: {report.summary.get('correct_family_selection')}",
            f"- Safety failures: {report.summary.get('safety_failures')}",
            "",
            "## Gates",
            "",
            "| Gate | Actual | Threshold | Pass |",
            "|------|--------|-----------|------|",
        ]
        for g in report.gates:
            lines.append(
                f"| {g['name']} | {g['actual']} | {g['threshold']} | "
                f"{'✅' if g['passed'] else '❌'} |"
            )
        lines.extend(["", "## Notes", "", "Developer diagnostics only — not user-facing.", ""])
        return "\n".join(lines)

    def _html(self, report: EvaluationReport) -> str:
        status = "BLOCKED" if report.release_blocked else "PASS"
        color = "#b42318" if report.release_blocked else "#027a48"
        rows = "".join(
            f"<tr><td>{g['name']}</td><td>{g['actual']}</td>"
            f"<td>{g['threshold']}</td><td>{'PASS' if g['passed'] else 'FAIL'}</td></tr>"
            for g in report.gates
        )
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Sarathi Benchmark — {report.product_release}</title>
  <style>
    body {{ font-family: Georgia, serif; margin: 2rem; color: #1a1a1a; background: #f7f4ef; }}
    h1 {{ font-weight: 600; }}
    .status {{ color: {color}; font-weight: 700; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; background: #fff; }}
    th, td {{ border: 1px solid #ddd; padding: 0.5rem 0.75rem; text-align: left; }}
    th {{ background: #efe8dc; }}
  </style>
</head>
<body>
  <h1>Sarathi Benchmark</h1>
  <p>{report.product_release} · {report.editorial_release}</p>
  <p>Release gate: <span class="status">{status}</span></p>
  <p>Avg editorial: {report.summary.get('avg_editorial_score')} ·
     Golden accuracy: {report.summary.get('golden_query_accuracy')}</p>
  <table>
    <thead><tr><th>Gate</th><th>Actual</th><th>Threshold</th><th>Result</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>
"""
