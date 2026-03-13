export type RawStepEvent = {
  step_name: string;
  step_status: string;
  attempt: number;
  started_at: string | null;
  ended_at: string | null;
  error_code: string | null;
};

export type StepGroup = {
  step_name: string;
  attempt: number;
  status: "RUNNING" | "COMPLETED" | "FAILED";
  start_time: string | null;
  end_time: string | null;
  raw_events: RawStepEvent[];
};

const PIPELINE_ORDER: Record<string, number> = {
  EXTRACTION: 1,
  INTERPRETATION: 2,
};

const FAILED_STATUS = "FAILED";
const SUCCEEDED_STATUS = "SUCCEEDED";

function parseTime(value: string | null): number | null {
  if (!value) {
    return null;
  }
  const parsed = Date.parse(value);
  if (Number.isNaN(parsed)) {
    return null;
  }
  return parsed;
}

function eventTimestamp(event: RawStepEvent): number | null {
  return parseTime(event.started_at) ?? parseTime(event.ended_at);
}

export function groupProcessingSteps(events: RawStepEvent[]): StepGroup[] {
  const grouped = new Map<string, RawStepEvent[]>();
  for (const event of events) {
    const attempt = event.attempt || 1;
    const key = `${event.step_name}::${attempt}`;
    const list = grouped.get(key);
    if (list) {
      list.push({ ...event, attempt });
    } else {
      grouped.set(key, [{ ...event, attempt }]);
    }
  }

  const groups: StepGroup[] = [];
  for (const [key, raw_events] of grouped.entries()) {
    const [step_name, attemptRaw] = key.split("::");
    const attempt = Number.parseInt(attemptRaw ?? "1", 10) || 1;
    const startedTimestamps = raw_events
      .map((event) => parseTime(event.started_at))
      .filter((value): value is number => value !== null);
    const endedTimestamps = raw_events
      .map((event) => parseTime(event.ended_at))
      .filter((value): value is number => value !== null);

    const start_time =
      startedTimestamps.length > 0
        ? new Date(Math.min(...startedTimestamps)).toISOString()
        : endedTimestamps.length > 0
          ? new Date(Math.min(...endedTimestamps)).toISOString()
          : null;

    const hasFailure = raw_events.some((event) => event.step_status === FAILED_STATUS);
    const hasSuccess = raw_events.some((event) => event.step_status === SUCCEEDED_STATUS);
    const status: StepGroup["status"] = hasFailure
      ? "FAILED"
      : hasSuccess
        ? "COMPLETED"
        : "RUNNING";

    const end_time =
      status === "RUNNING" || (endedTimestamps.length === 0 && startedTimestamps.length === 0)
        ? null
        : endedTimestamps.length > 0
          ? new Date(Math.max(...endedTimestamps)).toISOString()
          : startedTimestamps.length > 0
            ? new Date(Math.max(...startedTimestamps)).toISOString()
            : null;

    const ordered_raw = [...raw_events].sort((a, b) => {
      const timeA = eventTimestamp(a) ?? 0;
      const timeB = eventTimestamp(b) ?? 0;
      return timeA - timeB;
    });

    groups.push({
      step_name,
      attempt,
      status,
      start_time,
      end_time,
      raw_events: ordered_raw,
    });
  }

  return groups.sort((a, b) => {
    const timeA = parseTime(a.start_time) ?? 0;
    const timeB = parseTime(b.start_time) ?? 0;
    if (timeA !== timeB) {
      return timeA - timeB;
    }
    const orderA = PIPELINE_ORDER[a.step_name] ?? 99;
    const orderB = PIPELINE_ORDER[b.step_name] ?? 99;
    if (orderA !== orderB) {
      return orderA - orderB;
    }
    return a.attempt - b.attempt;
  });
}
