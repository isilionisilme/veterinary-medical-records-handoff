# Processing execution model (in-process)

## Asynchronous behavior
- API requests MUST NOT block on processing completion.
- Processing runs in background, in-process (task runner / executor / internal loop).

## Scheduler semantics
Authority: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B1.5 + B1.5.1.

Implementation guidance:
- Use a fixed tick with sleep (no busy-loop).
- Treat scheduler execution as best-effort and never block API request handling.

## Runner lifecycle (implementation)
- Start the scheduler as a long-lived background task from FastAPI lifespan/startup.
- Store the task handle on `app.state` so shutdown can cancel it.
- Loop behavior:
  - on each tick, attempt to start eligible queued runs (per Appendix B1.5.1),
  - apply the persistence guard pattern for `QUEUED → RUNNING` (Appendix B1.2.1),
  - log best-effort scheduler/step events per Appendix A8.1.
- Shutdown behavior:
  - cancel the task and await best-effort for a clean exit.
- Avoid event-loop blocking:
  - if a step performs blocking I/O or CPU-heavy work (e.g., PDF parsing), run it off the event loop (threadpool) so requests remain responsive.

## Crash recovery (startup)
On application startup:
- Any run found in `RUNNING` is considered orphaned.
- Transition it to `FAILED` with `failure_type = PROCESS_TERMINATED`.
- Emit log event `RUN_RECOVERED_AS_FAILED`.

Authority: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B1.3 + Appendix C3.

## Retry + timeout policy
Authority: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B1.4 + B1.4.1.

Implementation guidance:
- Retries are local to a single run and limited to the fixed default (no new runs).
- Timeouts transition the run to `TIMED_OUT` (terminal).
- Reprocessing always creates a **new** run.
