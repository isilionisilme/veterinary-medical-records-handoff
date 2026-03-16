# Architecture Overview

> One-page summary. For contracts and invariants see [technical-design.md](technical-design).

## Tech stack

| Layer        | Technology                               | Why                                                                                     |
| ------------ | ---------------------------------------- | --------------------------------------------------------------------------------------- |
| Frontend     | React 18 + TypeScript 5 + Tailwind CSS 3 | Type-safe SPA with utility-first styling                                                |
| Backend      | Python 3.11 + FastAPI 0.115              | Async-first framework, auto-generated OpenAPI                                           |
| Database     | SQLite (WAL mode)                        | Zero-config, ACID, portable — see [ADR-sqlite-database](ADR-sqlite-database) |
| PDF parsing  | PyMuPDF 1.24                             | High-fidelity text extraction with built-in fallback                                    |
| Unit testing | Vitest 4 + Pytest                        | Fast, parallel test runners for both stacks                                             |
| E2E testing  | Playwright 1.58                          | Cross-browser automation with trace/video on failure                                    |
| CI/CD        | GitHub Actions (10 jobs)                 | Path-filtered, cached, cancel-in-progress                                               |
| Containers   | Docker Compose                           | One-command `docker compose up --build`                                                 |

## System context

The system has a single external actor (the veterinarian/evaluator) and two
internal persistence boundaries.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef4ff","primaryTextColor":"#1f2937","primaryBorderColor":"#4f6df5","lineColor":"#64748b","secondaryColor":"#ffffff","tertiaryColor":"#f8fafc","clusterBkg":"#f8fafc","clusterBorder":"#cbd5e1","edgeLabelBackground":"#ffffff","fontFamily":"Segoe UI, sans-serif"},"flowchart":{"curve":"linear"}}}%%
graph LR
    User(("Veterinarian /<br/>Evaluator"))
    subgraph System["Veterinary Medical Records"]
        FE["Frontend SPA<br/>(React + TS)"]
        BE["Backend API<br/>(FastAPI)"]
        DB[("SQLite<br/>WAL mode")]
        FS[("File Storage<br/>(PDFs)")]
        FE -->|REST API| BE
        BE --> DB
        BE --> FS
    end
    User -->|HTTP| FE

    style User fill:#eef4ff,stroke:#4f6df5,color:#1f2937
    style FE fill:#eef4ff,stroke:#4f6df5,color:#1f2937
    style BE fill:#eef4ff,stroke:#4f6df5,color:#1f2937
    style DB fill:#ffffff,stroke:#cbd5e1,color:#1f2937
    style FS fill:#ffffff,stroke:#cbd5e1,color:#1f2937
    style System fill:#f8fafc,stroke:#cbd5e1,color:#475569
```

There are no external integrations, message queues, or third-party services.
The system is fully self-contained by design
([ADR-modular-monolith](ADR-modular-monolith),
[ADR-in-process-async-processing](ADR-in-process-async-processing)).

## System diagram

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef4ff","primaryTextColor":"#1f2937","primaryBorderColor":"#4f6df5","lineColor":"#64748b","secondaryColor":"#ffffff","tertiaryColor":"#f8fafc","clusterBkg":"#f8fafc","clusterBorder":"#cbd5e1","edgeLabelBackground":"#ffffff","fontFamily":"Segoe UI, sans-serif"},"flowchart":{"curve":"linear"}}}%%
graph TB
    subgraph "Frontend — React SPA"
        UI["AppWorkspace"]
        API["documentApi.ts"]
        UI --> API
    end

    subgraph "Backend — FastAPI"
        Routes["API Routes<br/>(5 domain modules)"]
        Services["Application Services<br/>(orchestrator, processing runner)"]
        Ports["Repository Protocol<br/>(DocumentRepository)"]
        SQLite[("SQLite DB<br/>WAL mode")]
        Storage[("File Storage<br/>(PDFs, artifacts)")]
        Routes --> Services
        Services --> Ports
        Ports --> SQLite
        Ports --> Storage
    end

    subgraph "Processing Pipeline"
        Extraction["PDF Extraction<br/>(PyMuPDF)"]
        Interpretation["Field Interpretation<br/>(candidate mining + scoring)"]
        Confidence["Confidence Scoring<br/>(band policy v1)"]
        Extraction --> Interpretation
        Interpretation --> Confidence
    end

    API -- "REST /api/*" --> Routes
    Services --> Extraction

    style UI fill:#eef4ff,stroke:#4f6df5,color:#1f2937
    style API fill:#eef4ff,stroke:#4f6df5,color:#1f2937
    style Routes fill:#eef4ff,stroke:#4f6df5,color:#1f2937
    style Services fill:#eef4ff,stroke:#4f6df5,color:#1f2937
    style Ports fill:#ffffff,stroke:#cbd5e1,color:#1f2937
    style SQLite fill:#ffffff,stroke:#cbd5e1,color:#1f2937
    style Storage fill:#ffffff,stroke:#cbd5e1,color:#1f2937
    style Extraction fill:#f8fafc,stroke:#94a3b8,color:#1f2937
    style Interpretation fill:#f8fafc,stroke:#94a3b8,color:#1f2937
    style Confidence fill:#f8fafc,stroke:#94a3b8,color:#1f2937
```

## Key architectural decisions

| Decision                     | Rationale                                                         | Record                                                            |
| ---------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------- |
| Modular monolith             | Single deploy, clear boundaries, Docker-first                     | [ADR-modular-monolith](ADR-modular-monolith)            |
| SQLite as primary DB         | Zero-config, ACID, portable; PostgreSQL migration path documented | [ADR-sqlite-database](ADR-sqlite-database)             |
| Raw SQL + repository pattern | Explicit queries, no ORM abstraction leaks                        | [ADR-raw-sql-repository-pattern](ADR-raw-sql-repository-pattern)  |
| In-process async processing  | No external queue for MVP; worker profile path documented         | [ADR-in-process-async-processing](ADR-in-process-async-processing) |

## Target architecture (beyond exercise scope)

The modular monolith implements a subset of a larger logical architecture designed for a production veterinary claims system. The full design includes 10 components organised around an event-driven backbone:

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef4ff","primaryTextColor":"#1f2937","primaryBorderColor":"#4f6df5","lineColor":"#64748b","secondaryColor":"#ffffff","tertiaryColor":"#f8fafc","clusterBkg":"#f8fafc","clusterBorder":"#cbd5e1","edgeLabelBackground":"#ffffff","fontFamily":"Segoe UI, sans-serif"},"flowchart":{"curve":"linear"}}}%%
graph TB
    subgraph ExerciseScope["Exercise Scope — Modular Monolith"]
        API["1. Claim API /<br/>Orchestrator"]
        SM["2. Claim State<br/>Machine"]
        EB["3. Event Bus /<br/>Queue"]
        ING["4. Document Ingestion<br/>& Canonicalisation"]
        EXT["5. Extraction<br/>Service"]
        UI["8. Veterinary Tool /<br/>Claims UI"]
    end

    POL["6. Policy Context Resolver<br/>+ Deterministic Rules Engine"]
    RAG["7. Assistive Reasoning<br/>Service (RAG)"]
    FB["9. Feedback &<br/>Evaluation Loop"]
    AN["10. Analytics &<br/>Data Pipelines"]

    UI -->|"Create / Update"| API
    API -->|"Trigger workflow"| SM
    SM -->|"Publish workflow"| EB
    EB -->|"Deliver workflow"| ING
    ING -->|"Publish document"| EXT
    EXT -->|"Deliver extracted claim"| UI
    EB -->|"Publish deterministic decision"| POL
    POL -->|"Resolve policy & rules"| EXT
    POL -->|"Escalate for interpretative reasoning"| RAG
    RAG -->|"Deliver assistive suggestions"| UI
    UI -->|"Publish decision feedback"| FB
    FB -->|"Publish quality & outcome metrics"| AN

    style ExerciseScope fill:#f8fafc,stroke:#4f6df5,color:#1f2937,stroke-width:2px
    style API fill:#eef4ff,stroke:#4f6df5,color:#1f2937
    style SM fill:#eef4ff,stroke:#4f6df5,color:#1f2937
    style EB fill:#eef4ff,stroke:#4f6df5,color:#1f2937
    style ING fill:#eef4ff,stroke:#4f6df5,color:#1f2937
    style EXT fill:#eef4ff,stroke:#4f6df5,color:#1f2937
    style UI fill:#eef4ff,stroke:#4f6df5,color:#1f2937
    style POL fill:#ffffff,stroke:#cbd5e1,color:#1f2937
    style RAG fill:#ffffff,stroke:#cbd5e1,color:#1f2937
    style FB fill:#ffffff,stroke:#cbd5e1,color:#1f2937
    style AN fill:#ffffff,stroke:#cbd5e1,color:#1f2937
```

Components inside the red boundary (1-5, 8) are implemented in the exercise as modules within the monolith. Components outside (6, 7, 9, 10) represent the production evolution — policy engine, RAG-assisted reasoning, feedback loop, and analytics pipelines. The modular monolith preserves module boundaries that map directly to these future services, making the transition incremental rather than a rewrite.

## Data flow

1. **Upload** → PDF stored on disk, metadata in SQLite, processing queued in-process
2. **Extract** → Text extraction via PyMuPDF with built-in fallback for edge cases
3. **Interpret** → Field identification via regex + candidate mining + confidence scoring
4. **Review** → Evaluator sees structured fields with confidence indicators, can edit/approve/reprocess

## Project structure

```text
backend/app/
├── api/           → 5 route modules (documents, review, processing, calibration, health)
├── application/   → orchestrator, processing runner, document services, extraction observability
│   └── processing/→ PDF extraction, interpretation, confidence scoring
├── domain/        → entities (models.py), status derivation
├── infra/         → SQLite repos (3 aggregates + façade), file storage
└── ports/         → repository protocols, file storage interface

frontend/src/
├── api/           → documentApi client
├── components/    → workspace/, viewer/, review/, structured/, ui/, app/, toast/
├── constants/     → shared constants
├── extraction/    → candidateSuggestions, fieldValidators
├── hooks/         → 28 production custom hooks for upload, review, rendering, sidebar, filters, and reprocessing flows
├── lib/           → utils, filters, validators
└── types/         → shared TypeScript interfaces
```

## Hexagonal component map

The backend follows a hexagonal (ports-and-adapters) architecture. Dependencies
point inward — outer layers depend on inner layers, never the reverse.

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef4ff","primaryTextColor":"#1f2937","primaryBorderColor":"#4f6df5","lineColor":"#64748b","secondaryColor":"#ffffff","tertiaryColor":"#f8fafc","clusterBkg":"#f8fafc","clusterBorder":"#cbd5e1","edgeLabelBackground":"#ffffff","fontFamily":"Segoe UI, sans-serif"},"flowchart":{"curve":"linear"}}}%%
graph TB
    subgraph API["api/ — Inbound adapters"]
        R1["routes_documents"]
        R2["routes_review"]
        R3["routes_processing"]
        R4["routes_calibration"]
        R5["routes_health"]
    end

    subgraph APP["application/ — Use cases"]
        SVC["document services<br/>(upload, query, edit, review)"]
        ORCH["orchestrator"]
        SCHED["scheduler"]
        PROC["processing pipeline<br/>(extraction, interpretation,<br/>candidate mining, confidence)"]
        OBS["extraction observability<br/>(snapshots, triage, ring buffer)"]
    end

    subgraph DOMAIN["domain/ — Core"]
        MOD["models & enums"]
        STATUS["status derivation"]
    end

    subgraph PORTS["ports/ — Interfaces"]
        REPO["DocumentRepository"]
        STORE["FileStorage"]
    end

    subgraph INFRA["infra/ — Outbound adapters"]
        SQL1["sqlite_document_repo"]
        SQL2["sqlite_run_repo"]
        SQL3["sqlite_calibration_repo"]
        FSIMPL["local_file_storage"]
        DB[("SQLite")]
        FS[("File System")]
    end

    API --> APP
    APP --> DOMAIN
    APP --> PORTS
    INFRA -.->|implements| PORTS
    SQL1 & SQL2 & SQL3 --> DB
    FSIMPL --> FS

    style API fill:#eef4ff,stroke:#4f6df5,color:#1f2937
    style APP fill:#eef4ff,stroke:#4f6df5,color:#1f2937
    style DOMAIN fill:#f8fafc,stroke:#4f6df5,color:#1f2937
    style PORTS fill:#ffffff,stroke:#cbd5e1,color:#1f2937
    style INFRA fill:#f8fafc,stroke:#94a3b8,color:#1f2937
```

<!-- Sources: backend/app/ directory structure -->

## Quality metrics (post-Iteration 12)

| Metric         | Value                      |
| -------------- | -------------------------- |
| Backend tests  | ~395 (≥91% coverage)       |
| Frontend tests | ~287 (≥87% coverage)       |
| E2E tests      | 65 (21 spec files)         |
| CI jobs        | 10 (path-filtered, ~4 min) |
| Lint errors    | 0                          |

## Scope boundaries

The following viewpoints are intentionally out of scope. Each
subsection documents the current state and what a production evolution would
require.

### Security (V7) — Out of scope

**Current state:**

- Optional static bearer token via `AUTH_TOKEN` env var (disabled when unset).
- Rate limiting on upload (10/min) and download (30/min) via `slowapi`.
- UUID validation on all path parameters.
- Non-root container execution.
- `pip-audit` and `npm audit` in CI.

**Production path:** OAuth 2.0 / JWT at API gateway, RBAC on endpoints, TLS
termination, STRIDE threat model, per-user quotas, audit logging. The hexagonal
architecture supports this without modifying domain or application layers.

### Operational concerns (V8) — Out of scope

**Current state:**

- 17 structured loggers via `getLogger(__name__)`.
- Health endpoint (`GET /health/ready`) with Docker healthcheck integration.
- Extraction observability ring buffer (20-run history per document).
- Build metadata embedded in image (`APP_VERSION`, `GIT_COMMIT`, `BUILD_DATE`).

**Production path:** Prometheus/OpenTelemetry metrics, structured JSON logging,
SLO definitions (availability, error rate, P95 latency), alerting rules,
operational runbooks (backup, DB maintenance, failure modes).

## Related documentation

- [technical-design.md](technical-design) — Contracts, state machines, API surface
- [product-design.md](product-design) — Product intent and semantics
- [ux-design.md](ux-design) — Interaction contract and confidence UX rules
- [implementation-history.md](implementation-history) — Incremental delivery timeline and metrics
- [ADR index](adr-index) — All architecture decision records
