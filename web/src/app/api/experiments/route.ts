import { NextResponse } from "next/server";

import { isDatabaseConfigured, listExperiments, saveExperiment } from "@/lib/experiment-store";
import type { ExperimentResult } from "@/lib/datasets";

export async function GET() {
  if (!isDatabaseConfigured()) return NextResponse.json({ experiments: [], persistenceEnabled: false });
  return NextResponse.json({ experiments: await listExperiments(), persistenceEnabled: true });
}

export async function POST(request: Request) {
  if (!isDatabaseConfigured()) {
    return NextResponse.json({ detail: "Experiment storage requires DATABASE_URL." }, { status: 503 });
  }
  const result = (await request.json()) as ExperimentResult;
  if (!result.dataset_name || !result.models?.length || !result.target_column) {
    return NextResponse.json({ detail: "A completed experiment result is required." }, { status: 400 });
  }
  const experiment = await saveExperiment(result);
  return NextResponse.json({ experiment }, { status: 201 });
}
