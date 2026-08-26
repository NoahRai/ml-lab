# ML Lab

ML Lab is an interactive experimentation platform that helps people upload tabular data, compare machine-learning models, inspect errors, and understand results in plain English.

> Screenshot / demo GIF placeholder

> Live demo placeholder

## Phase 1 status

This repository provides end-to-end tabular experiments: CSV inspection, target/task selection, and fair comparisons between linear/logistic regression, Random Forest, Gradient Boosting, and a PyTorch neural network with a leakage-safe 80/20 split. Storage and AI explanations are deliberate later phases.

## Architecture

```mermaid
graph LR
  A[Next.js client] --> B[Next.js web/API layer]
  B -->|ML_API_URL| C[FastAPI ML service]
  B -. future .-> D[(PostgreSQL)]
  B -. future .-> E[LLM API]
```

The ML service is separate so Vercel can host the web product while longer-running Python workloads can be deployed to a suitable container host. The web layer will use `ML_API_URL`, avoiding provider-specific coupling.

## Repository layout

```text
web/          Next.js App Router frontend
ml-service/   FastAPI machine-learning service
```

## Local development

### Web

```bash
cd web
npm run dev
```

### ML service

```bash
cd ml-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/health` to confirm the service is healthy.

### PostgreSQL persistence

Set `DATABASE_URL` to a Supabase Postgres or another PostgreSQL database, then run:

```bash
cd web
npm run db:generate
npm run db:migrate -- --name init
```

Saved experiments store metadata, model metrics, settings, and result artifacts; raw uploaded CSV bytes are not persisted in the relational database.

### AI explanations

Set `OPENAI_API_KEY` (and optionally `OPENAI_MODEL`) on the web server to enable **Explain My Results**. The API receives only a structured summary of computed metrics, model timings, feature-importance values, and error counts—not the raw CSV. Its prompt explicitly prohibits inventing experiment facts and separates results from hypotheses.

## API (Phase 1)

`GET /health`

```json
{ "status": "healthy", "service": "ml-service" }
```

`POST /dataset/analyze` accepts a CSV upload and returns dataset dimensions, missing-value counts, detected column types, target candidates, and a safe 15-row preview. The service enforces 10 MB, 50,000-row, and 100-column limits.

`POST /experiment/run` accepts a CSV, target column, problem type, and model list. It uses a consistent reproducible split, fits preprocessing only on training rows, and returns each model's real test metrics.

Planned endpoint: `POST /predict`.

## ML pipeline roadmap

The next phase validates CSVs and returns a dataset preview. The first complete training slice will support linear/logistic regression. Preprocessing will be fitted on training data only to prevent leakage, and later models will share a `BaseMLModel` interface via a factory.

## Testing

```bash
cd ml-service
pytest
```

## Deployment

Deploy `web/` to Vercel. Build and deploy `ml-service/` from its Dockerfile to a container host, then set `ML_API_URL` in the web environment. Do not commit secrets; use `.env.example` as the key reference.

### Production checklist

1. Deploy `web/` to Vercel and set `ML_API_URL`, `DATABASE_URL`, and Supabase/OpenAI variables only in the platform environment.
2. Deploy `ml-service/` from its Dockerfile to a container host and set `ML_ALLOWED_ORIGINS` to the Vercel domain.
3. Run Prisma migrations against the production PostgreSQL database before enabling saved experiments.
4. Configure Google OAuth redirect URLs in Supabase for the production URL.
5. The ML service enforces file, row, column, and model-count limits and uses a per-instance request limit. For multi-instance production scale, replace the in-memory limiter with Redis or a platform rate-limiting service.

## Future improvements

- CSV inspection and robust validation
- Regression and classification experiment pipeline
- Model comparison, error analysis, and feature importance
- PostgreSQL-backed saved experiments and authentication
- Grounded AI explanations using structured experiment results
