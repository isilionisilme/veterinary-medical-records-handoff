import { describe, expect, it } from "vitest";

import { mapDocumentStatus } from "./documentStatus";
import { groupProcessingSteps, type RawStepEvent } from "./processingHistory";
import {
  formatDuration,
  formatShortDate,
  formatTime,
  shouldShowDetails,
  statusIcon,
} from "./processingHistoryView";

describe("mapDocumentStatus", () => {
  it("returns error when backend status is FAILED", () => {
    const status = mapDocumentStatus({
      status: "FAILED",
      failure_type: null,
    });

    expect(status).toEqual({
      label: "Error",
      tone: "error",
      tooltip: "El documento tuvo un error durante el procesamiento.",
      icon: "dot",
    });
  });

  it("prioritizes failure_type over reviewed/completed", () => {
    const status = mapDocumentStatus({
      status: "COMPLETED",
      failure_type: "OCR_FAILURE",
      review_status: "REVIEWED",
    });

    expect(status.label).toBe("Error");
    expect(status.tone).toBe("error");
  });

  it("returns reviewed cluster when reviewed without failures", () => {
    const status = mapDocumentStatus({
      status: "COMPLETED",
      failure_type: null,
      review_status: "REVIEWED",
    });

    expect(status).toEqual({
      label: "Revisado",
      tone: "success",
      tooltip: "Documento revisado. Usa Reabrir para volver a editar.",
      icon: "check",
    });
  });

  it("returns listo when completed and not reviewed", () => {
    const status = mapDocumentStatus({
      status: "COMPLETED",
      failure_type: null,
      review_status: "PENDING",
    });

    expect(status.label).toBe("Listo");
    expect(status.tone).toBe("success");
  });

  it("returns processing cluster for in-progress states", () => {
    const status = mapDocumentStatus({
      status: "PROCESSING",
      failure_type: null,
    });

    expect(status.label).toBe("Procesando");
    expect(status.tone).toBe("warn");
  });
});

describe("groupProcessingSteps", () => {
  it("groups events by step+attempt and applies status precedence", () => {
    const events: RawStepEvent[] = [
      {
        step_name: "EXTRACTION",
        step_status: "RUNNING",
        attempt: 1,
        started_at: "2026-02-20T10:00:00.000Z",
        ended_at: null,
        error_code: null,
      },
      {
        step_name: "EXTRACTION",
        step_status: "FAILED",
        attempt: 1,
        started_at: null,
        ended_at: "2026-02-20T10:01:00.000Z",
        error_code: "E_TIMEOUT",
      },
    ];

    const groups = groupProcessingSteps(events);
    expect(groups).toHaveLength(1);
    expect(groups[0]).toMatchObject({
      step_name: "EXTRACTION",
      attempt: 1,
      status: "FAILED",
      start_time: "2026-02-20T10:00:00.000Z",
      end_time: "2026-02-20T10:01:00.000Z",
    });
    expect(groups[0].raw_events).toHaveLength(2);
  });

  it("keeps RUNNING status and null end_time when no success/failure exists", () => {
    const events: RawStepEvent[] = [
      {
        step_name: "INTERPRETATION",
        step_status: "RUNNING",
        attempt: 1,
        started_at: "2026-02-20T10:05:00.000Z",
        ended_at: null,
        error_code: null,
      },
    ];

    const [group] = groupProcessingSteps(events);
    expect(group.status).toBe("RUNNING");
    expect(group.end_time).toBeNull();
  });

  it("sorts by start time and uses pipeline order as tie-breaker", () => {
    const events: RawStepEvent[] = [
      {
        step_name: "INTERPRETATION",
        step_status: "SUCCEEDED",
        attempt: 1,
        started_at: "2026-02-20T10:00:00.000Z",
        ended_at: "2026-02-20T10:02:00.000Z",
        error_code: null,
      },
      {
        step_name: "EXTRACTION",
        step_status: "SUCCEEDED",
        attempt: 1,
        started_at: "2026-02-20T10:00:00.000Z",
        ended_at: "2026-02-20T10:01:00.000Z",
        error_code: null,
      },
      {
        step_name: "EXTRACTION",
        step_status: "SUCCEEDED",
        attempt: 2,
        started_at: "2026-02-20T10:03:00.000Z",
        ended_at: "2026-02-20T10:04:00.000Z",
        error_code: null,
      },
    ];

    const groups = groupProcessingSteps(events);
    expect(groups.map((group) => `${group.step_name}:${group.attempt}`)).toEqual([
      "EXTRACTION:1",
      "INTERPRETATION:1",
      "EXTRACTION:2",
    ]);
    expect(groups[0].status).toBe("COMPLETED");
  });

  it("falls back to ended_at when started_at is missing", () => {
    const events: RawStepEvent[] = [
      {
        step_name: "EXTRACTION",
        step_status: "SUCCEEDED",
        attempt: 1,
        started_at: null,
        ended_at: "2026-02-20T10:01:00.000Z",
        error_code: null,
      },
    ];

    const [group] = groupProcessingSteps(events);
    expect(group.start_time).toBe("2026-02-20T10:01:00.000Z");
    expect(group.end_time).toBe("2026-02-20T10:01:00.000Z");
  });
});

describe("processingHistoryView helpers", () => {
  it("formats short date and time in UTC", () => {
    const value = "2026-02-21T14:05:00.000Z";
    expect(formatShortDate(value)).toBe("21/02/26");
    expect(formatTime(value)).toBe("14:05");
  });

  it("returns null for invalid or empty date/time values", () => {
    expect(formatShortDate(null)).toBeNull();
    expect(formatShortDate("invalid")).toBeNull();
    expect(formatTime(null)).toBeNull();
    expect(formatTime("invalid")).toBeNull();
  });

  it("formats duration with <1s and second buckets", () => {
    expect(formatDuration("2026-02-21T10:00:00.000Z", "2026-02-21T10:00:00.500Z")).toBe("<1s");
    expect(formatDuration("2026-02-21T10:00:00.000Z", "2026-02-21T10:00:07.000Z")).toBe("7s");
  });

  it("returns null for invalid duration inputs", () => {
    expect(formatDuration(null, "2026-02-21T10:00:01.000Z")).toBeNull();
    expect(formatDuration("invalid", "2026-02-21T10:00:01.000Z")).toBeNull();
    expect(formatDuration("2026-02-21T10:00:02.000Z", "2026-02-21T10:00:01.000Z")).toBeNull();
  });

  it("maps icons and details visibility consistently", () => {
    expect(statusIcon("FAILED")).toBe("❌");
    expect(statusIcon("COMPLETED")).toBe("✅");
    expect(statusIcon("RUNNING")).toBe("⏳");

    expect(
      shouldShowDetails({
        step_name: "EXTRACTION",
        attempt: 1,
        status: "FAILED",
        start_time: null,
        end_time: null,
        raw_events: [],
      }),
    ).toBe(true);
    expect(
      shouldShowDetails({
        step_name: "EXTRACTION",
        attempt: 2,
        status: "COMPLETED",
        start_time: null,
        end_time: null,
        raw_events: [],
      }),
    ).toBe(true);
    expect(
      shouldShowDetails({
        step_name: "INTERPRETATION",
        attempt: 1,
        status: "COMPLETED",
        start_time: null,
        end_time: null,
        raw_events: [],
      }),
    ).toBe(false);
  });
});
