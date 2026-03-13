import type { ReactNode } from "react";

type StructuredDataViewProps = {
  children?: ReactNode;
};

export function StructuredDataView({ children }: StructuredDataViewProps) {
  return <>{children ?? null}</>;
}
