type VisitScopedFieldLike = {
  key?: string;
};

export type VisitGroupLike = {
  visit_id?: string | null;
  fields?: VisitScopedFieldLike[] | null;
};

export type VisitGroupingDiagnostics = {
  visits_count: number;
  unassigned_present: boolean;
  fields_per_visit: Record<string, number>;
  total_visit_scoped_fields_count: number;
  all_visit_scoped_in_unassigned: boolean;
};

function normalizeVisitId(visitId: string | null | undefined, fallbackIndex: number): string {
  const trimmed = typeof visitId === "string" ? visitId.trim() : "";
  if (trimmed.length > 0) {
    return trimmed;
  }
  return `visit_${fallbackIndex + 1}`;
}

function isUnassignedVisitId(visitId: string): boolean {
  return visitId.trim().toLowerCase() === "unassigned";
}

export function buildVisitGroupingDiagnostics(visits: VisitGroupLike[]): VisitGroupingDiagnostics {
  const fieldsPerVisit: Record<string, number> = {};
  let totalVisitScopedFieldsCount = 0;
  let unassignedVisitScopedFieldsCount = 0;

  visits.forEach((visit, index) => {
    const visitId = normalizeVisitId(visit.visit_id, index);
    const fieldCount = Array.isArray(visit.fields) ? visit.fields.length : 0;
    fieldsPerVisit[visitId] = fieldCount;
    totalVisitScopedFieldsCount += fieldCount;
    if (isUnassignedVisitId(visitId)) {
      unassignedVisitScopedFieldsCount += fieldCount;
    }
  });

  return {
    visits_count: visits.length,
    unassigned_present: visits.some((visit, index) =>
      isUnassignedVisitId(normalizeVisitId(visit.visit_id, index)),
    ),
    fields_per_visit: fieldsPerVisit,
    total_visit_scoped_fields_count: totalVisitScopedFieldsCount,
    all_visit_scoped_in_unassigned:
      totalVisitScopedFieldsCount > 0 &&
      totalVisitScopedFieldsCount === unassignedVisitScopedFieldsCount,
  };
}

export function shouldEmitVisitGroupingDiagnostics(env: { DEV?: boolean; MODE?: string }): boolean {
  return Boolean(env.DEV && env.MODE !== "test");
}
