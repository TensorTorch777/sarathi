"use client";

import { useEffect, useState } from "react";

type Gate = {
  name: string;
  passed: boolean;
  actual: number | boolean;
  threshold: number | boolean;
};

type TrustReport = {
  generated_at: string;
  editorial_release: string;
  product_release: string;
  release_blocked: boolean;
  summary: Record<string, number>;
  gates: Gate[];
  evaluations?: Array<{
    response_level: string;
    journey_used: boolean;
    retrieval_confidence: number;
    overall_score: number;
    safety_score: { passed: boolean };
    editorial_score: { mean: number };
    family: string | null;
  }>;
};

export default function TrustDashboardPage() {
  const [report, setReport] = useState<TrustReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/trust/latest.json")
      .then(async (res) => {
        if (!res.ok) {
          throw new Error("Trust report not generated yet. Run `make eval`.");
        }
        return res.json();
      })
      .then(setReport)
      .catch((err: Error) => setError(err.message));
  }, []);

  if (error) {
    return (
      <main className="mx-auto min-h-screen max-w-4xl px-6 py-12 text-[var(--ink)]">
        <h1 className="font-[family-name:var(--font-display)] text-3xl text-[var(--gold-soft)]">
          Trust Dashboard
        </h1>
        <p className="mt-4 text-[var(--ink-muted)]">{error}</p>
      </main>
    );
  }

  if (!report) {
    return (
      <main className="mx-auto min-h-screen max-w-4xl px-6 py-12 text-[var(--ink)]">
        <h1 className="font-[family-name:var(--font-display)] text-3xl text-[var(--gold-soft)]">
          Trust Dashboard
        </h1>
        <p className="mt-4 text-[var(--ink-muted)]">Loading evaluation snapshot…</p>
      </main>
    );
  }

  const levels = report.evaluations ?? [];
  const l1 = levels.filter((e) => e.response_level === "L1").length;
  const l2 = levels.filter((e) => e.response_level === "L2").length;
  const l3 = levels.filter((e) => e.response_level === "L3").length;
  const journeys = levels.filter((e) => e.journey_used).length;
  const safetyHits = levels.filter((e) => !e.safety_score.passed).length;
  const avgConf =
    levels.length === 0
      ? 0
      : levels.reduce((s, e) => s + e.retrieval_confidence, 0) / levels.length;

  const stats = [
    ["Avg editorial score", fmt(report.summary.avg_editorial_score)],
    ["Avg overall score", fmt(report.summary.avg_overall_score)],
    ["Golden accuracy", pct(report.summary.golden_query_accuracy)],
    ["Family accuracy", pct(report.summary.correct_family_selection)],
    ["Avg retrieval confidence", pct(avgConf)],
    ["Journey offers/uses", String(journeys)],
    ["Safety interventions", String(safetyHits)],
    ["Levels L1/L2/L3", `${l1}/${l2}/${l3}`],
  ] as const;

  return (
    <main className="mx-auto min-h-screen max-w-4xl px-6 py-12 text-[var(--ink)]">
      <p className="text-xs uppercase tracking-[0.12em] text-[var(--ink-muted)]">
        Read-only · Developer / ops
      </p>
      <h1 className="mt-2 font-[family-name:var(--font-display)] text-4xl font-medium text-[var(--gold-soft)]">
        Trust Dashboard
      </h1>
      <p className="mt-3 max-w-xl text-[var(--ink-muted)]">
        Measurable wisdom quality for {report.product_release}. Editorial corpus:{" "}
        {report.editorial_release}.
      </p>
      <p
        className={`mt-4 font-semibold ${
          report.release_blocked ? "text-[var(--danger)]" : "text-[var(--success)]"
        }`}
      >
        Release gate: {report.release_blocked ? "BLOCKED" : "PASS"}
      </p>
      <p className="text-sm text-[var(--ink-faint)]">Generated {report.generated_at}</p>

      <section className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {stats.map(([label, value]) => (
          <div
            key={label}
            className="rounded-xl border border-[var(--glass-border)] bg-[var(--bg-panel)] px-4 py-3"
          >
            <div className="text-xs text-[var(--ink-muted)]">{label}</div>
            <div className="mt-1 font-[family-name:var(--font-display)] text-xl text-[var(--gold-soft)]">
              {value}
            </div>
          </div>
        ))}
      </section>

      <section className="mt-10">
        <h2 className="font-[family-name:var(--font-display)] text-2xl text-[var(--ink)]">
          Release gates
        </h2>
        <div className="mt-3 overflow-hidden rounded-xl border border-[var(--glass-border)]">
          <table className="w-full text-left text-sm">
            <thead className="bg-[rgba(212,175,55,0.08)] text-[var(--gold-soft)]">
              <tr>
                <th className="px-3 py-2 font-medium">Gate</th>
                <th className="px-3 py-2 font-medium">Actual</th>
                <th className="px-3 py-2 font-medium">Threshold</th>
                <th className="px-3 py-2 font-medium">Result</th>
              </tr>
            </thead>
            <tbody>
              {report.gates.map((g) => (
                <tr key={g.name} className="border-t border-[rgba(255,255,255,0.06)]">
                  <td className="px-3 py-2">{g.name}</td>
                  <td className="px-3 py-2">{String(g.actual)}</td>
                  <td className="px-3 py-2">{String(g.threshold)}</td>
                  <td
                    className={`px-3 py-2 font-medium ${
                      g.passed ? "text-[var(--success)]" : "text-[var(--danger)]"
                    }`}
                  >
                    {g.passed ? "PASS" : "FAIL"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="mt-10">
        <h2 className="font-[family-name:var(--font-display)] text-2xl">
          Editorial score distribution
        </h2>
        <ul className="mt-4 space-y-2">
          {(report.evaluations ?? []).slice(0, 12).map((e, i) => (
            <li
              key={`${e.family}-${i}`}
              className="grid grid-cols-[10rem_1fr_3rem] items-center gap-3 text-sm"
            >
              <span className="truncate text-[var(--ink-muted)]">{e.family ?? "unknown"}</span>
              <span className="h-1.5 overflow-hidden rounded-full bg-[rgba(255,255,255,0.06)]">
                <span
                  className="block h-full rounded-full bg-gradient-to-r from-[var(--gold-dim)] to-[var(--gold)]"
                  style={{ width: `${Math.round((e.editorial_score.mean || 0) * 100)}%` }}
                />
              </span>
              <span>{fmt(e.editorial_score.mean)}</span>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}

function fmt(n: number | undefined) {
  if (typeof n !== "number" || Number.isNaN(n)) return "—";
  return n.toFixed(2);
}

function pct(n: number | undefined) {
  if (typeof n !== "number" || Number.isNaN(n)) return "—";
  return `${Math.round(n * 100)}%`;
}
