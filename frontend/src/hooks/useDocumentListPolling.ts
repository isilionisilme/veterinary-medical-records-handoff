import { type Dispatch, type SetStateAction, useEffect, useMemo, useRef } from "react";
import { useQuery } from "@tanstack/react-query";

import { fetchDocuments } from "../api/documentApi";
import { isDocumentProcessing } from "../lib/appWorkspaceUtils";

type UseDocumentListPollingParams = {
  setIsDocsSidebarHovered: Dispatch<SetStateAction<boolean>>;
};

export function useDocumentListPolling({ setIsDocsSidebarHovered }: UseDocumentListPollingParams) {
  const listPollingStartedAtRef = useRef<number | null>(null);

  const documentList = useQuery({
    queryKey: ["documents", "list"],
    queryFn: fetchDocuments,
  });

  const sortedDocuments = useMemo(() => {
    const items = documentList.data?.items ?? [];
    return [...items].sort((a, b) => {
      const aTime = Date.parse(a.created_at);
      const bTime = Date.parse(b.created_at);
      if (Number.isNaN(aTime) && Number.isNaN(bTime)) {
        return a.document_id.localeCompare(b.document_id);
      }
      if (Number.isNaN(aTime)) {
        return 1;
      }
      if (Number.isNaN(bTime)) {
        return -1;
      }
      return bTime - aTime;
    });
  }, [documentList.data?.items]);

  const documentListItems = useMemo(
    () => documentList.data?.items ?? [],
    [documentList.data?.items],
  );
  const refetchDocumentList = documentList.refetch;

  useEffect(() => {
    const items = documentListItems;
    const processingItems = items.filter((item) => isDocumentProcessing(item.status));
    if (processingItems.length === 0) {
      listPollingStartedAtRef.current = null;
      return;
    }
    const now = Date.now();
    if (listPollingStartedAtRef.current === null) {
      listPollingStartedAtRef.current = now;
    }
    const elapsedMs = now - listPollingStartedAtRef.current;
    const maxPollingWindowMs = 10 * 60 * 1000;
    if (elapsedMs > maxPollingWindowMs) {
      return;
    }
    const intervalMs = elapsedMs < 2 * 60 * 1000 ? 1500 : 5000;
    const intervalId = window.setInterval(() => {
      refetchDocumentList();
    }, intervalMs);
    return () => window.clearInterval(intervalId);
  }, [refetchDocumentList, documentListItems]);

  useEffect(() => {
    if (documentList.status !== "success") {
      return;
    }
    if (sortedDocuments.length === 0) {
      setIsDocsSidebarHovered(false);
    }
  }, [documentList.status, setIsDocsSidebarHovered, sortedDocuments.length]);

  return { documentList, sortedDocuments };
}
