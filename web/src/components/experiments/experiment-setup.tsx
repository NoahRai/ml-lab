"use client";

import { ChangeEvent, FormEvent, useState } from "react";
import Link from "next/link";

import type { DatasetAnalysis, DatasetApiError, ExperimentResult, ProblemType } from "@/lib/datasets";

const MAX_FILE_BYTES = 10 * 1024 * 1024;
const modelOptions = [
  { id: "linear", label: "Linear / Logistic Regression", description: "A fast, interpretable baseline." },
  { id: "random_forest", label: "Random Forest", description: "An ensemble for nonlinear patterns." },
  { id: "gradient_boosting", label: "Gradient Boosting", description: "A strong tree-based baseline." },
];

function formatNumber(value: number) {
  return new Intl.NumberFormat("en-US").format(value);
}

export function ExperimentSetup() {
  const [file, setFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<DatasetAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [target, setTarget] = useState("");
  const [problemType, setProblemType] = useState<ProblemType>("classification");
  const [result, setResult] = useState<ExperimentResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [selectedModels, setSelectedModels] = useState<string[]>(["linear", "random_forest", "gradient_boosting"]);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0] ?? null;
    setAnalysis(null);
    setResult(null);
    setTarget("");
    setError(null);
    if (!selected) return setFile(null);
    if (!selected.name.toLowerCase().endsWith(".csv")) {
      setFile(null);
      return setError("Please choose a CSV file.");
    }
    if (selected.size > MAX_FILE_BYTES) {
      setFile(null);
      return setError("This file is larger than the 10 MB upload limit.");
    }
    setFile(selected);
  }

  async function analyze(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) return setError("Choose a CSV file to continue.");
    setIsAnalyzing(true);
    setError(null);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await fetch("/api/datasets/analyze", { method: "POST", body: formData });
      const payload: DatasetAnalysis | DatasetApiError = await response.json();
      if (!response.ok) throw new Error("detail" in payload ? payload.detail : "We couldn't inspect this dataset.");
      const nextAnalysis = payload as DatasetAnalysis;
      setAnalysis(nextAnalysis);
      setResult(null);
      setTarget(nextAnalysis.potential_target_columns.at(-1) ?? "");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "We couldn't inspect this dataset.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  async function runBaseline() {
    if (!file || !target) return setError("Choose a target column before running the experiment.");
    setIsRunning(true);
    setError(null);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("target_column", target);
    formData.append("problem_type", problemType);
    selectedModels.forEach((modelType) => formData.append("model_types", modelType));
    try {
      const response = await fetch("/api/experiments/run", { method: "POST", body: formData });
      const payload: ExperimentResult | DatasetApiError = await response.json();
      if (!response.ok) throw new Error("detail" in payload ? payload.detail : "We couldn't run this experiment.");
      setResult(payload as ExperimentResult);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "We couldn't run this experiment.");
    } finally {
      setIsRunning(false);
    }
  }

  function toggleModel(modelType: string) {
    setResult(null);
    setSelectedModels((current) => current.includes(modelType) ? current.filter((item) => item !== modelType) : [...current, modelType]);
  }

  return (
    <main className="min-h-screen bg-[#fafaf9] text-[#161614]">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5 lg:px-8"><Link className="flex items-center gap-2.5 font-semibold" href="/"><span className="grid h-8 w-8 place-items-center rounded-lg bg-[#161614] text-sm text-white">M</span>ML Lab</Link><span className="text-sm text-[#74736c]">New experiment</span></header>
      <div className="mx-auto grid max-w-6xl gap-10 px-6 pb-20 pt-12 lg:grid-cols-[0.65fr_1.35fr] lg:px-8">
        <aside><p className="text-xs font-semibold tracking-[0.15em] text-[#697b68]">STEP 1 OF 3</p><h1 className="mt-4 text-4xl font-semibold tracking-[-0.045em]">Set up your dataset.</h1><p className="mt-4 max-w-sm leading-7 text-[#706f68]">Upload a CSV and we&apos;ll identify usable features before you choose a prediction task.</p><ol className="mt-10 space-y-4 text-sm"><li className="font-medium">01 · Dataset</li><li className="text-[#a09f98]">02 · Configure</li><li className="text-[#a09f98]">03 · Choose models</li></ol></aside>
        <section className="rounded-2xl border border-[#e3e2dc] bg-white p-6 shadow-sm sm:p-8">
          <form onSubmit={analyze}>
            <label className="block text-sm font-semibold" htmlFor="dataset">Upload a CSV</label><p className="mt-1 text-sm text-[#77766f]">Up to 10 MB · 50,000 rows · 100 columns</p>
            <div className="mt-5 rounded-xl border border-dashed border-[#cfcfc7] bg-[#fafbf8] p-7 text-center"><input id="dataset" className="mx-auto block max-w-full text-sm" type="file" accept=".csv,text/csv" onChange={handleFileChange} /><p className="mt-4 text-sm text-[#696861]">{file ? file.name : "Choose a file from your computer"}</p></div>
            {error && <p className="mt-4 rounded-lg bg-[#fcf1ef] px-3 py-2.5 text-sm text-[#9b3a2e]" role="alert">{error}</p>}
            <button className="mt-5 rounded-lg bg-[#161614] px-4 py-2.5 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50" disabled={!file || isAnalyzing} type="submit">{isAnalyzing ? "Inspecting dataset…" : "Inspect dataset"}</button>
          </form>

          {analysis && <div className="mt-10 border-t border-[#e9e8e3] pt-8"><div className="flex flex-wrap items-end justify-between gap-3"><div><p className="text-xs font-semibold tracking-[0.14em] text-[#697b68]">DATASET OVERVIEW</p><h2 className="mt-2 text-2xl font-semibold tracking-tight">{analysis.filename}</h2></div><span className="text-sm text-[#717069]">Ready to configure</span></div><div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">{[["Rows", formatNumber(analysis.rows)], ["Columns", analysis.columns], ["Numerical", analysis.numeric_columns.length], ["Missing", `${analysis.missing_percentage}%`]].map(([label, value]) => <div key={String(label)} className="rounded-lg bg-[#f5f6f2] p-3"><p className="text-xs text-[#77766f]">{label}</p><p className="mt-1 text-xl font-semibold">{value}</p></div>)}</div>
            <div className="mt-8 grid gap-5 border-t border-[#e9e8e3] pt-7 sm:grid-cols-2"><label className="text-sm font-medium">Target column<select className="mt-2 block w-full rounded-lg border border-[#dcdad3] bg-white px-3 py-2.5 text-sm" value={target} onChange={(event) => setTarget(event.target.value)}>{analysis.potential_target_columns.map((column) => <option key={column}>{column}</option>)}</select></label><label className="text-sm font-medium">Problem type<select className="mt-2 block w-full rounded-lg border border-[#dcdad3] bg-white px-3 py-2.5 text-sm" value={problemType} onChange={(event) => setProblemType(event.target.value as ProblemType)}><option value="classification">Classification</option><option value="regression">Regression</option></select></label></div>
            <fieldset className="mt-7 border-t border-[#e9e8e3] pt-7"><legend className="text-sm font-semibold">Models to compare</legend><p className="mt-1 text-sm text-[#77766f]">Each model uses the same held-out test data.</p><div className="mt-4 grid gap-3">{modelOptions.map((model) => <label className="flex cursor-pointer items-start gap-3 rounded-lg border border-[#e1e0da] p-3 has-[:checked]:border-[#7d967b] has-[:checked]:bg-[#f6f9f5]" key={model.id}><input className="mt-1" checked={selectedModels.includes(model.id)} onChange={() => toggleModel(model.id)} type="checkbox" /><span><span className="block text-sm font-medium">{model.label}</span><span className="mt-0.5 block text-xs text-[#74736c]">{model.description}</span></span></label>)}</div></fieldset>
            <div className="mt-5 flex items-center justify-between gap-4 rounded-xl bg-[#f5f6f2] p-4"><p className="text-sm leading-6 text-[#62625b]">Run a reproducible 80/20 train/test comparison.</p><button className="shrink-0 rounded-lg bg-[#161614] px-4 py-2.5 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50" disabled={!target || !selectedModels.length || isRunning} onClick={runBaseline} type="button">{isRunning ? "Training models…" : "Run experiment"}</button></div>
            {result && <section className="mt-8 rounded-xl border border-[#dbe3d8] bg-[#f8fbf7] p-5"><p className="text-xs font-semibold tracking-[0.14em] text-[#5f7a5e]">EXPERIMENT RESULT</p><div className="mt-3 flex flex-wrap items-end justify-between gap-4"><div><h3 className="text-xl font-semibold">Best: {result.best_model}</h3><p className="mt-1 text-sm text-[#65655e]">Trained on {formatNumber(result.training_rows)} rows · evaluated on {formatNumber(result.testing_rows)} held-out rows</p></div><div className="text-right"><p className="text-3xl font-semibold tracking-tight">{result.primary_metric_value.toFixed(4)}</p><p className="text-xs uppercase tracking-wide text-[#6c6b64]">best {result.primary_metric_name}</p></div></div><div className="mt-5 overflow-x-auto"><table className="w-full min-w-max text-left text-sm"><thead className="border-y border-[#dce4d9] text-[#626c60]"><tr><th className="px-3 py-2 font-medium">Model</th><th className="px-3 py-2 font-medium">{result.primary_metric_name}</th><th className="px-3 py-2 font-medium">Training</th></tr></thead><tbody>{result.models.map((model) => <tr className="border-b border-[#e6ece4]" key={model.name}><td className="px-3 py-2 font-medium">{model.name}</td><td className="px-3 py-2">{model.metrics[result.primary_metric_name].toFixed(4)}</td><td className="px-3 py-2">{model.training_time_ms.toFixed(1)} ms</td></tr>)}</tbody></table></div><p className="mt-4 text-xs leading-5 text-[#6d706a]">{result.notes[0]}</p></section>}
            <div className="mt-8 overflow-x-auto"><h3 className="text-sm font-semibold">Column details</h3><table className="mt-3 w-full min-w-max text-left text-sm"><thead className="border-y border-[#e8e7e1] text-[#66655e]"><tr><th className="px-3 py-2 font-medium">Column</th><th className="px-3 py-2 font-medium">Type</th><th className="px-3 py-2 font-medium">Unique</th><th className="px-3 py-2 font-medium">Missing</th><th className="px-3 py-2 font-medium">Statistics</th></tr></thead><tbody>{analysis.column_summaries.map((column) => <tr className="border-b border-[#f0efea]" key={column.name}><td className="px-3 py-2 font-medium">{column.name}</td><td className="px-3 py-2 capitalize text-[#575650]">{column.kind}</td><td className="px-3 py-2 text-[#575650]">{formatNumber(column.unique_count)}</td><td className="px-3 py-2 text-[#575650]">{formatNumber(column.missing_count)}</td><td className="px-3 py-2 text-[#575650]">{column.mean === null ? "—" : `min ${column.minimum} · avg ${column.mean} · max ${column.maximum}`}</td></tr>)}</tbody></table></div>
            <div className="mt-8 overflow-x-auto"><h3 className="text-sm font-semibold">Preview</h3><table className="mt-3 w-full min-w-max text-left text-sm"><thead className="border-y border-[#e8e7e1] text-[#66655e]"><tr>{analysis.column_summaries.map((column) => <th className="px-3 py-2 font-medium" key={column.name}>{column.name}</th>)}</tr></thead><tbody>{analysis.preview.map((row, index) => <tr className="border-b border-[#f0efea]" key={index}>{analysis.column_summaries.map((column) => <td className="px-3 py-2 text-[#575650]" key={column.name}>{row[column.name] === null ? "—" : String(row[column.name])}</td>)}</tr>)}</tbody></table></div>
          </div>}
        </section>
      </div>
    </main>
  );
}
