# IMPLEMENTATION_PLAN — Modules

This content was split into smaller modules for token-optimized assistant reads.

Start with `AGENTS.md` (repo root) and `docs/agent_router/00_AUTHORITY.md` for intent routing.

## Index
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/10_preamble.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/20_purpose.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/30_how-to-use-this-document.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/40_contract-boundary-non-negotiable.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/50_scope.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/60_execution-rules.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/65_add-user-story-workflow.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/70_release-1-document-upload-access.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/80_release-2-automatic-processing-traceability.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/90_release-3-extraction-transparency-trust-debuggability.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/100_release-4-assisted-review-in-context-high-value-higher-risk.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/110_release-5-editing-learning-signals-human-corrections.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/120_release-6-explicit-overrides-workflow-closure.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/130_release-7-edit-workflow-hardening.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/131_release-8-evidence-navigation-document-interaction.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/132_release-9-extraction-quality-language.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/133_release-10-ux-polish-upload-ergonomics.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/134_release-11-help-content-externalization-i18n.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/135_release-12-additional-formats-ocr.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/136_release-13-schema-evolution-isolated-reviewer-workflows.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/137_release-14-research-operational-readiness.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/150_us-01-upload-document.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/160_us-02-view-document-status.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/170_us-03-download-preview-original-document.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/180_us-04-list-uploaded-documents-and-their-status.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/190_us-05-process-document.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/200_us-21-upload-medical-documents.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/210_us-11-view-document-processing-history.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/220_us-06-view-extracted-text.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/230_us-07-review-document-in-context.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/240_us-08-edit-structured-data.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/250_us-09-capture-correction-signals.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/260_us-10-change-document-language-and-reprocess.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/270_us-12-mark-document-as-reviewed.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/275_us-32-align-review-rendering-to-global-schema-template.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/276_us-35-resizable-splitter-between-pdf-viewer-and-structured-data-panel.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/277_us-41-show-top-5-candidate-suggestions-in-field-edit-modal.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/278_us-42-provide-evaluator-friendly-installation-execution-docker-first.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/278a_us-44-medical-record-mvp-update-extracted-data-panel-structure-labels-and-scope.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/279_us-43-render-visitas-agrupadas-contract-driven-no-heuristics.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/279a_us-45-visit-detection-mvp-deterministic-contract-driven-coverage-improvement.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/279b_us-46-deterministic-visit-assignment-coverage-mvp-schema.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/280_us-13-review-aggregated-pending-structural-changes.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/290_us-14-filter-and-prioritize-pending-structural-changes.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/300_us-15-approve-structural-changes-into-the-global-schema.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/310_us-16-reject-or-defer-structural-changes.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/320_us-17-govern-critical-non-reversible-structural-changes.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/330_us-18-audit-trail-of-schema-governance-decisions.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/340_us-19-add-docx-end-to-end-support.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/350_us-20-add-images-end-to-end-support.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/351_us-47-prevent-losing-unsaved-field-edits.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/352_us-48-reset-fields-to-original-detected-value.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/353_us-49-treat-save-of-originally-suggested-value-as-unmodified.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/354_us-59-refresh-visible-confidence-after-edits-on-reopened-document.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/355_us-50-navigate-to-and-highlight-field-evidence.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/356_us-51-text-search-in-pdf-viewer.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/357_us-52-improve-visit-detection-heuristics.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/358_us-53-improve-general-extraction-heuristics.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/359_us-54-patient-history-summary-field-antecedentes.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/360_us-55-contextual-help-icons-with-wiki-links.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/361_us-56-externalize-ui-texts-to-editable-files.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/362_us-57-research-field-standardization.md`
- `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/363_us-58-define-production-db-reset-policy.md`

## Propagated updates
- Story status propagation requires `**Status**: Implemented (YYYY-MM-DD)` updates in the implementation plan when explicitly requested.

### Confidence-related propagation
- US-38 reviewed-toggle workflow and US-39 confidence-policy alignment are tracked as authoritative story-level contracts in this owner module family.
- US-40 field-level confidence tooltip breakdown is tracked as a dedicated story-level contract in this owner module family.
- US-59 refresh visible confidence after edits on reopened document is tracked as a dedicated story-level contract in this owner module family.
- US-33 is marked implemented with status date `2026-02-13` in the source plan.

### Release reorganization (2026-02-24)
- Old R7 (Schema evolution) → R13, old R8 (Additional formats) → R12, post-MVP section eliminated.
- New R7 (Edit workflow hardening), R8 (Evidence navigation), R9 (Extraction quality), R10 (UX polish), R11 (Help/i18n), R14 (Research) added.
- New stories: US-47 through US-59 (13 stories total).
- US-27 renamed to "Add in-app help wiki and entry point" with expanded scope.

### Traceability expansion (2026-03-07)
- Source implementation plan now documents the US-61 through US-78 traceability block, including US-78 processing history planning links.

### Multi-visit plan series normalization (2026-03-07)
- Source implementation plan references the renamed multi-visit plan files: `COMPLETED_2026-03-06_MULTI-VISIT_P1_RAWTEXT-BOUNDARIES.md`, `COMPLETED_2026-03-07_MULTI-VISIT_P2_PER-VISIT-FIELD-EXTRACTION.md`, and `PLAN_2026-03-07_MULTI-VISIT_P3_VISIT-SCOPING-OBSERVABILITY.md`.
