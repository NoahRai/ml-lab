import { NextResponse } from "next/server";

import { isDatabaseConfigured, listExperiments, saveExperiment } from "@/lib/experiment-store";
import type { ExperimentResult } from "@/lib/datasets";
import { getCurrentUser } from "@/lib/supabase/server";

export async function GET() {
  if (!isDatabaseConfigured()) return NextResponse.json({ experiments: [], persistenceEnabled: false });
  const user = await getCurrentUser();
  if (!user) return NextResponse.json({ experiments: [], persistenceEnabled: true, authenticated: false });
  return NextResponse.json({ experiments: await listExperiments(user.id), persistenceEnabled: true, authenticated: true });
}

export async function POST(request: Request) {
  if (!isDatabaseConfigured()) {
    return NextResponse.json({ detail: "Experiment storage requires DATABASE_URL." }, { status: 503 });
  }
  const user = await getCurrentUser();
  if (!user?.email) return NextResponse.json({ detail: "Sign in to save experiments." }, { status: 401 });
  const result = (await request.json()) as ExperimentResult;
  if (!result.dataset_name || !result.models?.length || !result.target_column) {
    return NextResponse.json({ detail: "A completed experiment result is required." }, { status: 400 });
  }
  const experiment = await saveExperiment(result, { id: user.id, email: user.email, name: user.user_metadata.full_name ?? null });
  return NextResponse.json({ experiment }, { status: 201 });
}
