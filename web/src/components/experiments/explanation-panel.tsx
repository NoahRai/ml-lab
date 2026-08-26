"use client";

import { FormEvent, useState } from "react";

import type { ExperimentResult } from "@/lib/datasets";

interface ExplanationPanelProps {
  result: ExperimentResult;
}

export function ExplanationPanel({ result }: ExplanationPanelProps) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function requestExplanation(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setError("");
    try {
      const response = await fetch("/api/experiments/explain", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ result, question }),
      });
      const payload = (await response.json()) as { explanation?: string; detail?: string };
      if (!response.ok || !payload.explanation) throw new Error(payload.detail ?? "We couldn't generate an explanation.");
      setAnswer(payload.explanation);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "We couldn't generate an explanation.");
    } finally {
      setIsLoading(false);
    }
  }

  return <section className="rounded-xl border border-[#dbe3d8] bg-[#f8fbf7] p-5"><p className="text-xs font-semibold tracking-[0.14em] text-[#5f7a5e]">EXPLAIN MY RESULTS</p><h3 className="mt-2 text-lg font-semibold">Ask about this experiment</h3><p className="mt-1 text-sm leading-6 text-[#65655e]">Answers receive only your computed experiment summary—not the raw CSV—and distinguish facts from hypotheses.</p><form className="mt-4 flex flex-col gap-3 sm:flex-row" onSubmit={requestExplanation}><input className="min-w-0 flex-1 rounded-lg border border-[#d5d9d1] bg-white px-3 py-2.5 text-sm" maxLength={500} onChange={(event) => setQuestion(event.target.value)} placeholder="Why did this model perform best?" value={question} /><button className="rounded-lg bg-[#161614] px-4 py-2.5 text-sm font-medium text-white disabled:opacity-50" disabled={isLoading} type="submit">{isLoading ? "Thinking…" : question ? "Ask" : "Explain results"}</button></form>{error && <p className="mt-3 text-sm text-[#9b3a2e]">{error}</p>}{answer && <div className="mt-5 whitespace-pre-wrap rounded-lg bg-white p-4 text-sm leading-6 text-[#3f403b]">{answer}</div>}</section>;
}
