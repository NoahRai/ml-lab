"use client";

import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts";

import type { ExperimentResult } from "@/lib/datasets";

interface ResultsDashboardProps {
  result: ExperimentResult;
}

function prettyMetric(metric: string) {
  return metric === "r2" ? "R²" : metric.toUpperCase();
}

export function ResultsDashboard({ result }: ResultsDashboardProps) {
  const modelPerformance = result.models.map((model) => ({ name: model.name.replace(" Regression", ""), value: model.metrics[result.primary_metric_name] }));
  const isRegression = result.problem_type === "regression";
  const neuralNetworkResult = result.models.find((model) => model.name === "Neural Network");

  return (
    <section className="mt-8 space-y-6 border-t border-[#e9e8e3] pt-8">
      <div className="rounded-xl border border-[#dbe3d8] bg-[#f8fbf7] p-5">
        <p className="text-xs font-semibold tracking-[0.14em] text-[#5f7a5e]">EXPERIMENT RESULT</p>
        <div className="mt-3 flex flex-wrap items-end justify-between gap-4"><div><h3 className="text-xl font-semibold">Best: {result.best_model}</h3><p className="mt-1 text-sm text-[#65655e]">{result.training_rows.toLocaleString()} training rows · {result.testing_rows.toLocaleString()} held-out test rows</p></div><div className="text-right"><p className="text-3xl font-semibold tracking-tight">{result.primary_metric_value.toFixed(4)}</p><p className="text-xs uppercase tracking-wide text-[#6c6b64]">best {prettyMetric(result.primary_metric_name)}</p></div></div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-[#e3e2dc] p-5"><h3 className="font-semibold">Model performance</h3><p className="mt-1 text-xs text-[#74736c]">Higher {prettyMetric(result.primary_metric_name)} is better.</p><div className="mt-5 h-56"><ResponsiveContainer width="100%" height="100%"><BarChart data={modelPerformance} layout="vertical" margin={{ left: 10 }}><CartesianGrid horizontal={false} stroke="#ecebe5" /><XAxis type="number" /><YAxis dataKey="name" type="category" width={100} tick={{ fontSize: 12 }} /><Tooltip /><Bar dataKey="value" fill="#6f8b6f" radius={[0, 4, 4, 0]} /></BarChart></ResponsiveContainer></div></div>
        <div className="rounded-xl border border-[#e3e2dc] p-5"><h3 className="font-semibold">Comparison</h3><div className="mt-4 overflow-x-auto"><table className="w-full min-w-max text-left text-sm"><thead className="border-y border-[#e8e7e1] text-[#66655e]"><tr><th className="px-2 py-2 font-medium">Model</th><th className="px-2 py-2 font-medium">{prettyMetric(result.primary_metric_name)}</th><th className="px-2 py-2 font-medium">Training</th></tr></thead><tbody>{result.models.map((model) => <tr className="border-b border-[#f0efea]" key={model.name}><td className="px-2 py-2 font-medium">{model.name}</td><td className="px-2 py-2">{model.metrics[result.primary_metric_name].toFixed(4)}</td><td className="px-2 py-2">{model.training_time_ms.toFixed(1)} ms</td></tr>)}</tbody></table></div></div>
      </div>

      {result.feature_importance.length > 0 && <div className="rounded-xl border border-[#e3e2dc] p-5"><h3 className="font-semibold">Feature importance</h3><p className="mt-1 text-xs text-[#74736c]">Importance reflects this model&apos;s learned patterns, not causation.</p><div className="mt-5 h-64"><ResponsiveContainer width="100%" height="100%"><BarChart data={result.feature_importance.map((item) => ({ ...item, importance: item.importance * 100 }))} layout="vertical" margin={{ left: 18 }}><CartesianGrid horizontal={false} stroke="#ecebe5" /><XAxis type="number" unit="%" /><YAxis dataKey="feature" type="category" width={125} tick={{ fontSize: 12 }} /><Tooltip formatter={(value) => `${Number(value ?? 0).toFixed(1)}%`} /><Bar dataKey="importance" fill="#9aa993" radius={[0, 4, 4, 0]} /></BarChart></ResponsiveContainer></div></div>}

      {neuralNetworkResult && neuralNetworkResult.training_history.length > 0 && <div className="rounded-xl border border-[#e3e2dc] p-5"><h3 className="font-semibold">Neural network learning curve</h3><p className="mt-1 text-xs text-[#74736c]">Training and validation loss by epoch. Training stops early when validation loss stops improving.</p><div className="mt-5 h-64"><ResponsiveContainer width="100%" height="100%"><LineChart data={neuralNetworkResult.training_history}><CartesianGrid stroke="#ecebe5" /><XAxis dataKey="epoch" /><YAxis /><Tooltip /><Legend /><Line dataKey="training_loss" dot={false} stroke="#6f8b6f" type="monotone" /><Line dataKey="validation_loss" dot={false} stroke="#b27d5c" type="monotone" /></LineChart></ResponsiveContainer></div></div>}

      {isRegression ? <div className="rounded-xl border border-[#e3e2dc] p-5"><h3 className="font-semibold">Actual vs. predicted</h3><p className="mt-1 text-xs text-[#74736c]">Each point is one held-out test prediction.</p><div className="mt-5 h-64"><ResponsiveContainer width="100%" height="100%"><ScatterChart margin={{ left: 5 }}><CartesianGrid stroke="#ecebe5" /><XAxis dataKey="actual" name="Actual" type="number" /><YAxis dataKey="predicted" name="Predicted" type="number" /><Tooltip cursor={{ strokeDasharray: "3 3" }} /><Scatter data={result.prediction_points} fill="#6f8b6f" /></ScatterChart></ResponsiveContainer></div></div> : result.confusion_matrix && <div className="rounded-xl border border-[#e3e2dc] p-5"><h3 className="font-semibold">Confusion matrix</h3><p className="mt-1 text-xs text-[#74736c]">Rows are actual classes; columns are predicted classes.</p><div className="mt-4 overflow-x-auto"><table className="text-center text-sm"><thead><tr><th className="p-2 text-left font-medium">Actual / predicted</th>{result.confusion_matrix.labels.map((label) => <th className="p-2 font-medium" key={label}>{label}</th>)}</tr></thead><tbody>{result.confusion_matrix.matrix.map((row, rowIndex) => <tr key={result.confusion_matrix?.labels[rowIndex]}><th className="p-2 text-left font-medium">{result.confusion_matrix?.labels[rowIndex]}</th>{row.map((value, columnIndex) => <td className="border border-[#e6e5df] bg-[#f5f7f3] p-2" key={columnIndex}>{value}</td>)}</tr>)}</tbody></table></div></div>}

      <div className="rounded-xl border border-[#e3e2dc] p-5"><h3 className="font-semibold">Error analysis</h3><p className="mt-1 text-xs text-[#74736c]">{isRegression ? "The largest absolute prediction errors on the held-out test set." : "Incorrect classifications from the held-out test set."}</p>{result.error_analysis.length === 0 ? <p className="mt-4 text-sm text-[#62625b]">No errors appeared in this test sample.</p> : <div className="mt-4 overflow-x-auto"><table className="w-full min-w-max text-left text-sm"><thead className="border-y border-[#e8e7e1] text-[#66655e]"><tr><th className="px-2 py-2 font-medium">Actual</th><th className="px-2 py-2 font-medium">Predicted</th>{isRegression && <th className="px-2 py-2 font-medium">Absolute error</th>}</tr></thead><tbody>{result.error_analysis.map((row, index) => <tr className="border-b border-[#f0efea]" key={index}><td className="px-2 py-2">{row.actual}</td><td className="px-2 py-2">{row.predicted}</td>{isRegression && <td className="px-2 py-2">{row.error?.toFixed(4)}</td>}</tr>)}</tbody></table></div>}</div>
      <p className="text-xs leading-5 text-[#6d706a]">{result.notes[0]}</p>
    </section>
  );
}
