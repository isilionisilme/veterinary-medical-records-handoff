import type { StepGroup } from "./processingHistory";

export function formatShortDate(value: string | null): string | null {
  if (!value) {
    return null;
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }
  const day = String(parsed.getUTCDate()).padStart(2, "0");
  const month = String(parsed.getUTCMonth() + 1).padStart(2, "0");
  const year = String(parsed.getUTCFullYear()).slice(-2);
  return `${day}/${month}/${year}`;
}

export function formatTime(value: string | null): string | null {
  if (!value) {
    return null;
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }
  const hours = String(parsed.getUTCHours()).padStart(2, "0");
  const minutes = String(parsed.getUTCMinutes()).padStart(2, "0");
  return `${hours}:${minutes}`;
}

export function formatDuration(startTime: string | null, endTime: string | null): string | null {
  if (!startTime || !endTime) {
    return null;
  }
  const start = new Date(startTime).getTime();
  const end = new Date(endTime).getTime();
  if (Number.isNaN(start) || Number.isNaN(end) || end < start) {
    return null;
  }
  const diffMs = end - start;
  if (diffMs < 1000) {
    return "<1s";
  }
  const seconds = Math.floor(diffMs / 1000);
  return `${seconds}s`;
}

export function statusIcon(status: StepGroup["status"]): string {
  if (status === "FAILED") {
    return "❌";
  }
  if (status === "COMPLETED") {
    return "✅";
  }
  return "⏳";
}

export function shouldShowDetails(step: StepGroup): boolean {
  return step.status === "FAILED" || step.attempt > 1;
}
