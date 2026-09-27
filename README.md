# Vera Engine — Deterministic Decision & Messaging Server

Vera Engine is a fast, rule-based, deterministic messaging and decision engine built with Python 3.11, FastAPI, Pydantic v2, and SQLite (WAL mode).

---

## Architecture Principles

- **No Fabrication**: Decisions and facts originate strictly from deterministic 4-context data (`Category`, `Merchant`, `Trigger`, `Customer`).
- **Determinism**: Same context + same state = same output. No non-deterministic LLM calls in the decision hot-path.
- **Durable Statefulness**: Context versioning, suppression logs, and conversation threads persist in a single-file SQLite database with WAL mode enabled.
- **Zero URL Policy**: Body text is cleaned of external URLs to avoid penalties.
- **Idempotent Versioning**: Idempotency rules enforced via `POST /v1/context`. Re-pushing existing/stale versions returns `409 Conflict`.

---

## Repository Layout

```
vera-engine/
├── app/
│   ├── main.py                  # FastAPI app & lifespan configuration
│   ├── config.py                 # Environment flags & metadata
│   ├── db.py                     # SQLite WAL mode initialization
│   ├── schemas/                  # Pydantic v2 lenient models
│   ├── store/                    # Versioned context, suppression & conversation persistence
│   ├── domain/                   # Extractors, categories, suppression rules & candidate scoring
│   ├── engine/                   # Decision engine & template composer
│   ├── reply/                    # Intent classifier & state machine
│   └── routes/                   # Endpoints: /v1/healthz, /v1/metadata, /v1/context, /v1/tick, /v1/reply
├── dataset/                      # Category definitions and seed data
├── generate_dataset.py           # Dataset expansion script
├── judge_simulator.py            # Local judge harness simulator
├── tests/                        # Pytest suite
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Local Setup & Testing

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Dataset
```bash
python generate_dataset.py --out ./expanded
```

### 3. Run Test Suite
```bash
pytest
```

### 4. Run Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### 5. Run Judge Simulator
```bash
python judge_simulator.py
```

---

## Docker Deployment

Build and run using Docker with persistent SQLite storage mounted at `/data/vera.db`:

```bash
docker build -t vera-engine .
docker run -p 8080:8080 -v vera_data:/data vera-engine
```
