import OpenAI from "openai";
import { NextResponse } from "next/server";

import { buildExperimentContext } from "@/lib/explanation-context";
import type { ExperimentResult } from "@/lib/datasets";

const instructions = `You explain machine-learning experiment results for a beginner. Use only the structured experiment context provided. Never invent metrics, data properties, feature effects, model behavior, or outcomes. Clearly label measured facts versus hypotheses: use phrases such as "The results show" for facts and "One possible explanation is" for hypotheses. Feature importance is not causation. Mention meaningful limitations and a next experiment when useful. Keep the answer concise and plain English.`;

export async function POST(request: Request) {
  if (!process.env.OPENAI_API_KEY) {
    return NextResponse.json({ detail: "AI explanations require OPENAI_API_KEY on the server." }, { status: 503 });
  }
  const body = (await request.json()) as { result?: ExperimentResult; question?: string };
  if (!body.result?.models?.length) {
    return NextResponse.json({ detail: "A completed experiment result is required." }, { status: 400 });
  }
  const question = body.question?.trim().slice(0, 500);
  const context = buildExperimentContext(body.result);
  const requestText = question
    ? `Question: ${question}\n\nExperiment context:\n${JSON.stringify(context)}`
    : `Explain this experiment in plain English:\n${JSON.stringify(context)}`;
  try {
    const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
    const response = await client.responses.create({
      model: process.env.OPENAI_MODEL ?? "gpt-5",
      instructions,
      input: requestText,
      store: false,
    });
    return NextResponse.json({ explanation: response.output_text });
  } catch {
    return NextResponse.json({ detail: "We couldn't generate an explanation right now. Try again shortly." }, { status: 502 });
  }
}
