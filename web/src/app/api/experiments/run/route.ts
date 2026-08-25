import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const formData = await request.formData();
  const file = formData.get("file");
  const targetColumn = formData.get("target_column");
  const problemType = formData.get("problem_type");

  if (!(file instanceof File) || typeof targetColumn !== "string" || typeof problemType !== "string") {
    return NextResponse.json({ detail: "Dataset, target column, and problem type are required." }, { status: 400 });
  }
  if (problemType !== "classification" && problemType !== "regression") {
    return NextResponse.json({ detail: "Problem type must be classification or regression." }, { status: 400 });
  }
  const serviceUrl = process.env.ML_API_URL;
  if (!serviceUrl) {
    return NextResponse.json({ detail: "The ML service URL is not configured." }, { status: 503 });
  }

  const upstreamData = new FormData();
  upstreamData.set("file", file, file.name);
  upstreamData.set("target_column", targetColumn);
  upstreamData.set("problem_type", problemType);
  upstreamData.set("train_split", "0.8");

  try {
    const response = await fetch(new URL("/experiment/run", serviceUrl), {
      method: "POST",
      body: upstreamData,
      cache: "no-store",
    });
    const payload: unknown = await response.json();
    return NextResponse.json(payload, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "We couldn't reach the ML service. Confirm it is running and try again." }, { status: 503 });
  }
}
