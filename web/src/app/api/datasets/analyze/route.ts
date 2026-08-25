import { NextResponse } from "next/server";

const MAX_FILE_BYTES = 10 * 1024 * 1024;

export async function POST(request: Request) {
  const formData = await request.formData();
  const file = formData.get("file");

  if (!(file instanceof File)) {
    return NextResponse.json({ detail: "Choose a CSV file to continue." }, { status: 400 });
  }
  if (!file.name.toLowerCase().endsWith(".csv")) {
    return NextResponse.json({ detail: "Please upload a CSV file with a .csv extension." }, { status: 422 });
  }
  if (file.size > MAX_FILE_BYTES) {
    return NextResponse.json({ detail: "This file is larger than the 10 MB upload limit." }, { status: 422 });
  }

  const serviceUrl = process.env.ML_API_URL;
  if (!serviceUrl) {
    return NextResponse.json(
      { detail: "The ML service URL is not configured. Set ML_API_URL and try again." },
      { status: 503 },
    );
  }

  const upstreamData = new FormData();
  upstreamData.set("file", file, file.name);

  try {
    const response = await fetch(new URL("/dataset/analyze", serviceUrl), {
      method: "POST",
      body: upstreamData,
      cache: "no-store",
    });
    const payload: unknown = await response.json();
    return NextResponse.json(payload, { status: response.status });
  } catch {
    return NextResponse.json(
      { detail: "We couldn't reach the ML service. Confirm it is running and try again." },
      { status: 503 },
    );
  }
}
