import { NextResponse } from "next/server";

const supportedDatasets = new Set(["iris", "wine"]);

export async function GET(_: Request, { params }: { params: Promise<{ datasetName: string }> }) {
  const { datasetName } = await params;
  if (!supportedDatasets.has(datasetName)) return NextResponse.json({ detail: "Demo dataset not found." }, { status: 404 });
  const serviceUrl = process.env.ML_API_URL;
  if (!serviceUrl) return NextResponse.json({ detail: "The ML service URL is not configured." }, { status: 503 });
  try {
    const response = await fetch(new URL(`/dataset/demo/${datasetName}`, serviceUrl), { cache: "no-store" });
    return new NextResponse(await response.text(), { status: response.status, headers: { "content-type": "text/csv; charset=utf-8" } });
  } catch {
    return NextResponse.json({ detail: "We couldn't reach the ML service." }, { status: 503 });
  }
}
