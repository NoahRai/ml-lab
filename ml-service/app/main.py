"""FastAPI entry point. ML execution endpoints are added in later phases."""

import logging
from time import perf_counter

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sklearn.datasets import load_iris, load_wine
from pydantic import BaseModel

from app.config import settings
from app.schemas.dataset import DatasetAnalysis
from app.schemas.experiment import ExperimentResult, ProblemType
from app.services.dataset_service import DatasetInspectionService, DatasetValidationError, UploadedDataset
from app.services.experiment_service import ExperimentService
from app.utils.rate_limit import InMemoryRateLimiter

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    status: str
    service: str


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="A provider-independent service boundary for ML Lab experiments.",
)
dataset_inspection_service = DatasetInspectionService()
experiment_service = ExperimentService()
rate_limiter = InMemoryRateLimiter()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["content-type"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started_at = perf_counter()
    response = await call_next(request)
    logger.info("request method=%s path=%s status=%s duration_ms=%.2f", request.method, request.url.path, response.status_code, (perf_counter() - started_at) * 1000)
    return response


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    """Return a lightweight readiness response without invoking ML dependencies."""
    return HealthResponse(status="healthy", service="ml-service")


@app.get("/dataset/demo/{dataset_name}", response_class=PlainTextResponse, tags=["datasets"])
def download_demo_dataset(dataset_name: str) -> str:
    """Provide safe bundled datasets without accepting or retaining user data."""
    datasets = {"iris": load_iris, "wine": load_wine}
    try:
        bundle = datasets[dataset_name](as_frame=True)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Demo dataset not found.") from error
    dataframe = bundle.frame.rename(columns={"target": "species" if dataset_name == "iris" else "wine_class"})
    if dataset_name == "iris":
        dataframe["species"] = dataframe["species"].map(dict(enumerate(bundle.target_names)))
    return dataframe.to_csv(index=False)


@app.post("/dataset/analyze", response_model=DatasetAnalysis, tags=["datasets"])
async def analyze_dataset(file: UploadFile = File(...), _: None = Depends(rate_limiter.check)) -> DatasetAnalysis:
    """Validate and inspect a CSV before it reaches the experiment pipeline."""
    try:
        return dataset_inspection_service.analyze(
            UploadedDataset(filename=file.filename or "upload.csv", content=await file.read())
        )
    except DatasetValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.post("/experiment/run", response_model=ExperimentResult, tags=["experiments"])
async def run_experiment(
    file: UploadFile = File(...),
    target_column: str = Form(...),
    problem_type: ProblemType = Form(...),
    train_split: float = Form(0.8),
    model_types: list[str] = Form(["linear"]),
    _: None = Depends(rate_limiter.check),
) -> ExperimentResult:
    """Train and evaluate a first baseline while keeping test data held out."""
    try:
        return experiment_service.run(
            UploadedDataset(filename=file.filename or "upload.csv", content=await file.read()),
            target_column=target_column,
            problem_type=problem_type,
            model_types=model_types,
            train_split=train_split,
        )
    except DatasetValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
