"""FastAPI entry point. ML execution endpoints are added in later phases."""

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.config import settings
from app.schemas.dataset import DatasetAnalysis
from app.services.dataset_service import DatasetInspectionService, DatasetValidationError, UploadedDataset


class HealthResponse(BaseModel):
    status: str
    service: str


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="A provider-independent service boundary for ML Lab experiments.",
)
dataset_inspection_service = DatasetInspectionService()


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    """Return a lightweight readiness response without invoking ML dependencies."""
    return HealthResponse(status="healthy", service="ml-service")


@app.post("/dataset/analyze", response_model=DatasetAnalysis, tags=["datasets"])
async def analyze_dataset(file: UploadFile = File(...)) -> DatasetAnalysis:
    """Validate and inspect a CSV before it reaches the experiment pipeline."""
    try:
        return dataset_inspection_service.analyze(
            UploadedDataset(filename=file.filename or "upload.csv", content=await file.read())
        )
    except DatasetValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
