# Step model 

## Step names (closed set)
Authority: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix C1.1 (StepName).

- `EXTRACTION`
- `INTERPRETATION`

## Step tracking via artifacts
Persist step lifecycle as append-only `Artifacts`:
- `artifact_type = STEP_STATUS`
- Payload schema is authoritative: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix C1.3.

## Failure mapping 
Authority: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix C3 (Error Codes and Failure Mapping).
