# Logging (structured) 

Each log entry MUST include:
- `document_id`
- `run_id` (nullable only when not yet created)
- `step_name` (nullable)
- `event_type`
- `timestamp`
- `error_code` (nullable)

Authority: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix A8.1 (Event Type Taxonomy).
