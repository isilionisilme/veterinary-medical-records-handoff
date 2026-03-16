# Staff Engineer Guide — Evaluator Edition

> **Audience**: Staff/principal engineers evaluating this codebase.
> **Reading time**: ~45 minutes.
> **Repository**: [veterinary-medical-records-handoff](https://github.com/isilionisilme/veterinary-medical-records-handoff) (Python 3.11 + TypeScript)

---

## 1. Executive Summary

This is a **veterinary medical records processing system** that extracts structured clinical data from PDF documents, assigns confidence scores to each field, and presents a side-by-side review interface where veterinarians correct and validate the extraction. The system owns the full lifecycle — from PDF upload through text extraction, candidate mining, confidence scoring, and human review — and delegates nothing to external services. There is no LLM: extraction and interpretation use deterministic regex-based pipelines with a calibration feedback loop.

The architecture is a **modular monolith** with hexagonal boundaries (ports & adapters), an in-process async scheduler, SQLite persistence, and a React/TanStack Query frontend. Every architectural choice — SQLite over PostgreSQL, in-process over Celery, raw SQL over ORM, bootstrap DDL over migrations — is captured in an ADR with explicit rationale and trade-off analysis.

---

## 2. The Core Architectural Insight

The most important concept in this system is that **confidence is not accuracy — it is operational consistency across similar contexts over time**.

A field with 0.85 confidence does not mean "85% chance of being correct." It means: "in documents with similar characteristics (type, language, clinic), this field has been consistently interpreted the same way."

```go
// Pseudocode (Go) — confidence is composed, not predicted
func computeFieldConfidence(candidate CandidateScore, calibration CalibrationAdjustment) float64 {
    base := candidate.PatternMatchScore  // how well regex matched
    adjustment := calibration.Delta       // bounded [-0.2, +0.2] from review history
    return clamp(base + adjustment, 0.0, 1.0)
}
```

This design choice — deterministic composition over ML prediction — means:
- Confidence is **reproducible**: same input → same score, always
- Confidence is **explainable**: tooltip breaks down candidate_confidence + review_adjustment
- Confidence **never blocks**: it guides attention, never prevents user action
- The system can evolve to ML-based scoring by replacing one module behind the port interface

<!-- Sources: backend/app/application/processing/confidence_scoring.py, backend/app/application/confidence_calibration.py, wiki/projects/01-product/product-design.md §6 -->

---

## 3. System Architecture

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#eef4ff","primaryTextColor":"#1f2937","primaryBorderColor":"#4f6df5","lineColor":"#64748b","secondaryColor":"#ffffff","tertiaryColor":"#f8fafc","clusterBkg":"#f8fafc","clusterBorder":"#cbd5e1","edgeLabelBackground":"#ffffff","fontFamily":"Segoe UI, sans-serif"},"flowchart":{"curve":"linear"}}}%%
graph TB
    subgraph CLIENT["Browser Client"]
        style CLIENT fill:#f8fafc,stroke:#cbd5e1,color:#1f2937
        FE["React SPA<br>TanStack Query"]
        style FE fill:#eef4ff,stroke:#4f6df5,color:#1f2937
    end

    subgraph API_LAYER["FastAPI Application"]
        style API_LAYER fill:#f8fafc,stroke:#cbd5e1,color:#1f2937
        ROUTES["Route Modules<br>6 domain modules"]
        DEPS["deps.py<br>DI Functions"]
        MW["Middleware Stack<br>CORS · Auth · Rate Limit<br>Body Limit · Correlation ID"]
        style ROUTES fill:#eef4ff,stroke:#4f6df5,color:#1f2937
        style DEPS fill:#eef4ff,stroke:#4f6df5,color:#1f2937
        style MW fill:#eef4ff,stroke:#4f6df5,color:#1f2937
