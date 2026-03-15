import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { useQueryClient } from "@tanstack/react-query";

import { type ActionFeedback, type UploadFeedback } from "../components/toast/toast-types";
import {
  API_BASE_URL,
  MAX_UPLOAD_SIZE_BYTES,
  REVIEW_MESSAGE_INFO_CLASS,
  REVIEW_MESSAGE_MUTED_CLASS,
  REVIEW_MESSAGE_WARNING_CLASS,
} from "../constants/appWorkspace";
import { useActiveDocumentQueries } from "../hooks/useActiveDocumentQueries";
import { useClinicAddressLookup } from "../hooks/useClinicAddressLookup";
import { useConfidenceDiagnostics } from "../hooks/useConfidenceDiagnostics";
import { useConnectivityToasts } from "../hooks/useConnectivityToasts";
import { useDocumentListPolling } from "../hooks/useDocumentListPolling";
import { useDocumentLoader } from "../hooks/useDocumentLoader";
import { useDocumentUpload } from "../hooks/useDocumentUpload";
import { useDocumentsSidebar } from "../hooks/useDocumentsSidebar";
import { useFieldEditing } from "../hooks/useFieldEditing";
import { useInterpretationEdit } from "../hooks/useInterpretationEdit";
import { useRawTextViewer } from "../hooks/useRawTextViewer";
import { useReprocessing } from "../hooks/useReprocessing";
import { useReviewDataPipeline } from "../hooks/useReviewDataPipeline";
import { useReviewPanelStatus } from "../hooks/useReviewPanelStatus";
import { useReviewRenderers } from "../hooks/useReviewRenderers";
import { useReviewSplitPanel } from "../hooks/useReviewSplitPanel";
import { useReviewToggle } from "../hooks/useReviewToggle";
import { useReviewedEditBlocker } from "../hooks/useReviewedEditBlocker";
import { useSourcePanelState } from "../hooks/useSourcePanelState";
import { useStructuredDataFilters } from "../hooks/useStructuredDataFilters";
import { useUploadState } from "../hooks/useUploadState";
import {
  formatRunHeader,
  formatTimestamp,
  getTechnicalDetails,
  getUserErrorMessage,
  isConnectivityOrServerError,
  isDocumentProcessing,
  isProcessingTooLong,
} from "../lib/appWorkspaceUtils";
import { mapDocumentStatus } from "../lib/documentStatus";
import { type ReviewSelectableField, type ReviewVisitGroup } from "../types";

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

function useWorkspaceValue() {
  // ── Core UI state ───────────────────────────────────────────────────────
  const [activeId, setActiveId] = useState<string | null>(null);
  const [activeViewerTab, setActiveViewerTab] = useState<"document" | "raw_text" | "technical">(
    "document",
  );
  const [expandedSteps, setExpandedSteps] = useState<Record<string, boolean>>({});
  const [uploadFeedback, setUploadFeedback] = useState<UploadFeedback | null>(null);
  const [actionFeedback, setActionFeedback] = useState<ActionFeedback | null>(null);
  const [showRefreshFeedback, setShowRefreshFeedback] = useState(false);
  const [selectedFieldId, setSelectedFieldId] = useState<string | null>(null);
  const [evidenceNotice, setEvidenceNotice] = useState<string | null>(null);
  const [expandedFieldValues, setExpandedFieldValues] = useState<Record<string, boolean>>({});
  const [fieldNavigationRequestId, setFieldNavigationRequestId] = useState(0);
  const [hoveredFieldTriggerId, setHoveredFieldTriggerId] = useState<string | null>(null);
  const [hoveredCriticalTriggerId, setHoveredCriticalTriggerId] = useState<string | null>(null);

  const refreshFeedbackTimerRef = useRef<number | null>(null);
  const queryClient = useQueryClient();

  // ── Connectivity ────────────────────────────────────────────────────────
  const {
    connectivityToast,
    showConnectivityToast,
    setConnectivityToast,
    hasShownListErrorToast,
    setHasShownListErrorToast,
  } = useConnectivityToasts();

  // ── Document loading ────────────────────────────────────────────────────
  const { fileUrl, filename, requestPdfLoad, loadPdf, pendingAutoOpenDocumentIdRef } =
    useDocumentLoader({
      onUploadFeedback: setUploadFeedback,
    });

  // ── View mode constants ─────────────────────────────────────────────────
  const effectiveViewMode = "browse";
  const isReviewMode = false;
  const isBrowseMode = true;

  const downloadUrl = useMemo(() => {
    if (!activeId) return null;
    return `${API_BASE_URL}/documents/${activeId}/download?download=true`;
  }, [activeId]);

  // ── Cleanup helpers ─────────────────────────────────────────────────────
  const clearRefreshFeedbackTimer = useCallback(() => {
    const refreshTimer = refreshFeedbackTimerRef.current;
    if (refreshTimer) window.clearTimeout(refreshTimer);
  }, []);

  useEffect(() => {
    return () => {
      clearRefreshFeedbackTimer();
    };
  }, [clearRefreshFeedbackTimer]);

  // ── Upload ──────────────────────────────────────────────────────────────
  const { uploadMutation } = useDocumentUpload({
    requestPdfLoad,
    pendingAutoOpenDocumentIdRef,
    onUploadFeedback: setUploadFeedback,
    onSetActiveId: setActiveId,
    onSetActiveViewerTab: setActiveViewerTab,
  });

  const {
    fileInputRef,
    uploadPanelRef,
    isDragOverViewer,
    isDragOverSidebarUpload,
    sidebarUploadDragDepthRef,
    handleViewerDragEnter,
    handleViewerDragOver,
    handleViewerDragLeave,
    handleViewerDrop,
    handleSidebarUploadDragEnter,
    handleSidebarUploadDragOver,
    handleSidebarUploadDragLeave,
    handleSidebarUploadDrop: handleSidebarUploadDropInternal,
    handleOpenUploadArea,
    handleSidebarFileInputChange,
  } = useUploadState({
    isUploadPending: uploadMutation.isPending,
    maxUploadSizeBytes: MAX_UPLOAD_SIZE_BYTES,
    onQueueUpload: (file) => uploadMutation.mutate(file),
    onSetUploadFeedback: setUploadFeedback,
  });

  // ── Sidebar ─────────────────────────────────────────────────────────────
  const {
    isDesktopForPin,
    isDocsSidebarPinned,
    shouldUseHoverDocsSidebar,
    shouldAutoCollapseDocsSidebar,
    isDocsSidebarExpanded,
    setIsDocsSidebarHovered,
    handleDocsSidebarMouseEnter,
    handleDocsSidebarMouseLeave,
    handleToggleDocsSidebarPin,
    notifySidebarUploadDrop,
  } = useDocumentsSidebar({
    activeId,
    isDragOverSidebarUpload,
    sidebarUploadDragDepthRef,
  });

  const { documentList, sortedDocuments } = useDocumentListPolling({
    setIsDocsSidebarHovered,
  });

  const handleSidebarUploadDrop = useCallback(
    (event: Parameters<typeof handleSidebarUploadDropInternal>[0]) => {
      notifySidebarUploadDrop();
      handleSidebarUploadDropInternal(event);
    },
    [handleSidebarUploadDropInternal, notifySidebarUploadDrop],
  );

  // ── Review split panel ──────────────────────────────────────────────────
  const {
    reviewSplitLayoutStyle,
    handleReviewSplitGridRef,
    resetReviewSplitRatio,
    startReviewSplitDragging,
    handleReviewSplitKeyboard,
  } = useReviewSplitPanel({
    isDocsSidebarExpanded,
    isDocsSidebarPinned,
    shouldAutoCollapseDocsSidebar,
  });

  // ── Source panel ────────────────────────────────────────────────────────
  const sourcePanel = useSourcePanelState({
    isDesktopForPin,
    onNotice: setEvidenceNotice,
  });

  // ── Document selection ──────────────────────────────────────────────────
  const handleSelectDocument = useCallback(
    (docId: string) => {
      setActiveId(docId);
      requestPdfLoad(docId);
    },
    [requestPdfLoad],
  );

  useEffect(() => {
    if (activeViewerTab !== "document" || !activeId || fileUrl) return;
    requestPdfLoad(activeId);
  }, [activeViewerTab, activeId, fileUrl, requestPdfLoad]);

  // ── Active document queries ─────────────────────────────────────────────
  const {
    documentDetails,
    processingHistory,
    documentReview,
    visitScopingMetrics,
    rawTextRunId,
    isProcessing,
    handleRefresh,
    isListRefreshing,
    clearRawTextRefreshKey,
  } = useActiveDocumentQueries({
    activeId,
    shouldFetchVisitScopingMetrics: activeViewerTab === "technical",
    documentList,
    showRefreshFeedback,
    setShowRefreshFeedback,
    refreshFeedbackTimerRef,
    queryClient,
  });

  // ── Raw text ────────────────────────────────────────────────────────────
  const {
    rawSearch,
    setRawSearch,
    rawSearchNotice,
    rawTextContent,
    hasRawText,
    canCopyRawText,
    isRawTextLoading,
    canSearchRawText,
    rawTextErrorMessage,
    handleRawSearch,
    copyFeedback,
    isCopyingRawText,
    handleDownloadRawText,
    handleCopyRawText,
  } = useRawTextViewer({ rawTextRunId, activeViewerTab });

  // ── Reset on active-id change ───────────────────────────────────────────
  const resetSourcePanel = sourcePanel.reset;
  useEffect(() => {
    setSelectedFieldId(null);
    setFieldNavigationRequestId(0);
    setEvidenceNotice(null);
    setExpandedFieldValues({});
    resetSourcePanel();
  }, [activeId, resetSourcePanel]);

  // ── Interpretation editing ──────────────────────────────────────────────
  const { interpretationEditMutation, submitInterpretationChanges } = useInterpretationEdit({
    activeId,
    reviewPayload: documentReview.data,
    onActionFeedback: setActionFeedback,
  });

  // ── Layout constants ────────────────────────────────────────────────────
  const panelHeightClass = "h-[clamp(720px,88vh,980px)]";

  const toggleStepDetails = useCallback((key: string) => {
    setExpandedSteps((prev) => ({ ...prev, [key]: !prev[key] }));
  }, []);

  // ── Derived document state ──────────────────────────────────────────────
  const activeListDocument = useMemo(
    () =>
      activeId
        ? (documentList.data?.items ?? []).find((item) => item.document_id === activeId)
        : null,
    [activeId, documentList.data?.items],
  );

  const activeReviewStatus =
    documentDetails.data?.review_status ?? activeListDocument?.review_status ?? "IN_REVIEW";
  const isDocumentReviewed = activeReviewStatus === "REVIEWED";
  const isActiveListProcessing = Boolean(
    activeListDocument && isDocumentProcessing(activeListDocument.status),
  );
  const isActiveDocumentProcessing = isProcessing || isActiveListProcessing;

  // ── Reprocessing ────────────────────────────────────────────────────────
  const {
    reprocessingDocumentId,
    hasObservedProcessingAfterReprocess,
    showRetryModal,
    setShowRetryModal,
    reprocessMutation,
    handleConfirmRetry,
  } = useReprocessing({
    activeId,
    isActiveDocumentProcessing,
    onActionFeedback: setActionFeedback,
    onReprocessSuccess: () => {
      clearRawTextRefreshKey();
    },
  });

  // ── Review toggle ───────────────────────────────────────────────────────
  const { reviewToggleMutation } = useReviewToggle({
    onActionFeedback: setActionFeedback,
  });

  const toggleReviewStatus = useCallback(() => {
    if (!activeId) return;
    reviewToggleMutation.mutate({
      docId: activeId,
      target: isDocumentReviewed ? "in_review" : "reviewed",
    });
  }, [activeId, isDocumentReviewed, reviewToggleMutation]);

  // ── Side-effect: toast auto-dismiss ─────────────────────────────────────
  useEffect(() => {
    if (!uploadFeedback) return;
    const timeoutMs = uploadFeedback.kind === "success" ? 3500 : 5000;
    const timer = window.setTimeout(() => setUploadFeedback(null), timeoutMs);
    return () => window.clearTimeout(timer);
  }, [uploadFeedback]);

  useEffect(() => {
    if (!actionFeedback) return;
    const timeoutMs = actionFeedback.kind === "success" ? 3500 : 5000;
    const timer = window.setTimeout(() => setActionFeedback(null), timeoutMs);
    return () => window.clearTimeout(timer);
  }, [actionFeedback]);

  // ── Side-effect: connectivity error handling ────────────────────────────
  useEffect(() => {
    if (documentList.isError) {
      if (isConnectivityOrServerError(documentList.error)) {
        showConnectivityToast();
        return;
      }
      if (!hasShownListErrorToast) {
        setUploadFeedback({
          kind: "error",
          message: getUserErrorMessage(documentList.error, "No se pudieron cargar los documentos."),
          technicalDetails: getTechnicalDetails(documentList.error),
        });
        setHasShownListErrorToast(true);
      }
      return;
    }
    if (documentList.isSuccess && hasShownListErrorToast) {
      setHasShownListErrorToast(false);
    }
  }, [
    documentList.isError,
    documentList.isSuccess,
    documentList.error,
    hasShownListErrorToast,
    setHasShownListErrorToast,
    showConnectivityToast,
  ]);

  useEffect(() => {
    if (
      !activeId ||
      !documentReview.isError ||
      !isConnectivityOrServerError(documentReview.error)
    ) {
      return;
    }
    showConnectivityToast();
  }, [
    activeId,
    documentReview.isError,
    documentReview.error,
    documentReview.errorUpdatedAt,
    documentReview.refetch,
    showConnectivityToast,
  ]);

  useEffect(() => {
    if (!loadPdf.isError || !isConnectivityOrServerError(loadPdf.error)) {
      return;
    }
    showConnectivityToast();
  }, [loadPdf.error, loadPdf.failureCount, loadPdf.isError, showConnectivityToast]);

  // ── Interpretation + canonical contract ─────────────────────────────────
  const interpretationData = documentReview.data?.active_interpretation.data;
  const schemaContract =
    typeof interpretationData?.schema_contract === "string"
      ? interpretationData.schema_contract.trim().toLowerCase()
      : null;
  const hasCanonicalContractSignal = schemaContract === "visit-grouped-canonical";
  const localIsCanonicalContract = hasCanonicalContractSignal;

  const localHasMalformedCanonicalFieldSlots = useMemo(() => {
    if (!localIsCanonicalContract) return false;
    return !Array.isArray(interpretationData?.medical_record_view?.field_slots);
  }, [interpretationData?.medical_record_view?.field_slots, localIsCanonicalContract]);

  const localReviewVisits = useMemo(
    () =>
      localIsCanonicalContract
        ? (interpretationData?.visits ?? []).filter((visit): visit is ReviewVisitGroup =>
            Boolean(visit && typeof visit === "object"),
          )
        : [],
    [interpretationData?.visits, localIsCanonicalContract],
  );

  // ── Confidence diagnostics ──────────────────────────────────────────────
  const { activeConfidencePolicy } = useConfidenceDiagnostics({
    interpretationData,
    reviewVisits: localReviewVisits,
    isCanonicalContract: localIsCanonicalContract,
  });

  // ── Structured data filters ─────────────────────────────────────────────
  const {
    structuredSearchInput,
    setStructuredSearchInput,
    selectedConfidenceBuckets,
    setSelectedConfidenceBuckets,
    showOnlyCritical,
    setShowOnlyCritical,
    showOnlyWithValue,
    setShowOnlyWithValue,
    showOnlyEmpty,
    setShowOnlyEmpty,
    structuredSearchInputRef,
    structuredDataFilters,
    hasActiveStructuredFilters,
    resetStructuredFilters,
    getFilterToggleItemClass,
  } = useStructuredDataFilters({ activeConfidencePolicy });

  // ── Review data pipeline ────────────────────────────────────────────────
  const {
    reportSections,
    selectableReviewItems,
    detectedFieldsSummary,
    reviewVisits,
    isCanonicalContract,
    hasMalformedCanonicalFieldSlots,
    hasVisitGroups,
    hasUnassignedVisitGroup,
    canonicalVisitFieldOrder,
    validatedReviewFields,
    buildSelectableField,
    visibleCoreGroups,
  } = useReviewDataPipeline({
    documentReview,
    interpretationData,
    isCanonicalContract: localIsCanonicalContract,
    hasMalformedCanonicalFieldSlots: localHasMalformedCanonicalFieldSlots,
    reviewVisits: localReviewVisits,
    activeConfidencePolicy,
    structuredDataFilters,
    hasActiveStructuredFilters,
  });

  // ── Selected field ──────────────────────────────────────────────────────
  const selectedReviewField = useMemo(() => {
    if (!selectedFieldId) return null;
    return selectableReviewItems.find((field) => field.id === selectedFieldId) ?? null;
  }, [selectableReviewItems, selectedFieldId]);

  // ── Review panel status ─────────────────────────────────────────────────
  const {
    reviewPanelState,
    reviewPanelMessage,
    shouldShowReviewEmptyState,
    hasNoStructuredFilterResults,
    isRetryingInterpretation,
    handleRetryInterpretation,
  } = useReviewPanelStatus({
    activeId,
    documentReview: {
      data: documentReview.data,
      isFetching: documentReview.isFetching,
      isError: documentReview.isError,
      error: documentReview.error,
      refetch: documentReview.refetch,
    },
    isActiveDocumentProcessing,
    hasActiveStructuredFilters,
    visibleCoreGroupsLength: visibleCoreGroups.length,
  });

  // ── Derived display constants ───────────────────────────────────────────
  const reviewMessageInfoClass = REVIEW_MESSAGE_INFO_CLASS;
  const reviewMessageMutedClass = REVIEW_MESSAGE_MUTED_CLASS;
  const reviewMessageWarningClass = REVIEW_MESSAGE_WARNING_CLASS;

  const shouldShowLoadPdfErrorBanner =
    loadPdf.isError && !isConnectivityOrServerError(loadPdf.error);

  const isPinnedSourcePanelVisible =
    isBrowseMode && sourcePanel.isSourceOpen && sourcePanel.isSourcePinned && isDesktopForPin;

  const isDocumentListConnectivityError =
    documentList.isError && isConnectivityOrServerError(documentList.error);

  // ── Review-item selection ───────────────────────────────────────────────
  const handleSelectReviewItem = useCallback((field: ReviewSelectableField) => {
    setSelectedFieldId(field.id);
    setFieldNavigationRequestId((current) => current + 1);
  }, []);

  const { handleReviewedEditAttempt, handleReviewedKeyboardEditAttempt } = useReviewedEditBlocker({
    isDocumentReviewed,
    onActionFeedback: setActionFeedback,
  });

  // ── Side-effect: stale field cleanup ────────────────────────────────────
  useEffect(() => {
    if (!selectedFieldId) return;
    const currentIds = new Set(selectableReviewItems.map((field) => field.id));
    if (!currentIds.has(selectedFieldId)) setSelectedFieldId(null);
  }, [selectableReviewItems, selectedFieldId]);

  useEffect(() => {
    if (!evidenceNotice) return;
    const timer = window.setTimeout(() => setEvidenceNotice(null), 3000);
    return () => window.clearTimeout(timer);
  }, [evidenceNotice]);

  // ── Field editing ───────────────────────────────────────────────────────
  const fieldEditing = useFieldEditing({
    onSubmitInterpretationChanges: submitInterpretationChanges,
    onActionFeedback: setActionFeedback,
  });

  const { lookupState, lookupResult, startLookup, acceptLookupResult, dismissLookup } =
    useClinicAddressLookup({
      onSubmitInterpretationChanges: submitInterpretationChanges,
      onActionFeedback: setActionFeedback,
    });

  const clinicEnrichmentContext = useMemo(() => {
    const clinicNameField = selectableReviewItems.find((f) => f.key === "clinic_name");
    const clinicAddressField = selectableReviewItems.find((f) => f.key === "clinic_address");
    const clinicNameValue =
      clinicNameField && !clinicNameField.isMissing
        ? String(clinicNameField.rawField?.value ?? "")
        : null;
    const addressIsMissing = clinicAddressField?.isMissing ?? true;
    if (!clinicNameValue || !addressIsMissing) return undefined;
    return {
      state: lookupState,
      foundAddress: lookupResult?.address ?? null,
      clinicNameValue,
      addressFieldItem: clinicAddressField ?? null,
      onSearch: () => {
        if (clinicAddressField) startLookup(clinicNameValue, clinicAddressField);
      },
      onAccept: acceptLookupResult,
      onDismiss: dismissLookup,
    };
  }, [
    selectableReviewItems,
    lookupState,
    lookupResult,
    startLookup,
    acceptLookupResult,
    dismissLookup,
  ]);

  // ── Review renderers ────────────────────────────────────────────────────
  const { renderSectionLayout } = useReviewRenderers({
    activeConfidencePolicy,
    isDocumentReviewed,
    isInterpretationEditPending: interpretationEditMutation.isPending,
    selectedFieldId,
    expandedFieldValues,
    hoveredFieldTriggerId,
    hoveredCriticalTriggerId,
    hasUnassignedVisitGroup,
    onOpenFieldEditDialog: fieldEditing.openFieldEditDialog,
    onSelectReviewItem: handleSelectReviewItem,
    onReviewedEditAttempt: handleReviewedEditAttempt,
    onReviewedKeyboardEditAttempt: handleReviewedKeyboardEditAttempt,
    onSetExpandedFieldValues: setExpandedFieldValues,
    onSetHoveredFieldTriggerId: setHoveredFieldTriggerId,
    onSetHoveredCriticalTriggerId: setHoveredCriticalTriggerId,
    clinicEnrichment: clinicEnrichmentContext,
    isCanonicalContract,
    hasVisitGroups,
    validatedReviewFields,
    reviewVisits,
    canonicalVisitFieldOrder,
    buildSelectableField,
  });

  // ── Error message strings ───────────────────────────────────────────────
  const loadPdfErrorMessage = getUserErrorMessage(
    loadPdf.error,
    "No se pudo cargar la vista previa del documento.",
  );
  const processingHistoryErrorMessage = getUserErrorMessage(
    processingHistory.error,
    "No se pudo cargar el historial de procesamiento.",
  );
  const visitScopingErrorMessage = getUserErrorMessage(
    visitScopingMetrics.error,
    "No pudimos cargar la observabilidad de visitas.",
  );

  // ── Derived values for DocumentsSidebar ─────────────────────────────────
  const isRefreshingDocuments = documentList.isFetching || showRefreshFeedback;
  const isDocumentListErrorVisible = documentList.isError && !isDocumentListConnectivityError;
  const documentListErrorMessage = isDocumentListErrorVisible
    ? getUserErrorMessage(documentList.error, "No se pudieron cargar los documentos.")
    : null;

  // ── Return ──────────────────────────────────────────────────────────────
  return {
    // Core UI state
    activeId,
    activeViewerTab,
    setActiveViewerTab,
    expandedSteps,
    uploadFeedback,
    actionFeedback,
    selectedFieldId,
    evidenceNotice,
    fieldNavigationRequestId,

    // Connectivity
    connectivityToast,
    setConnectivityToast,

    // Document loading
    fileUrl,
    filename,
    requestPdfLoad,
    loadPdf,
    downloadUrl,

    // View mode
    effectiveViewMode,
    isReviewMode,
    isBrowseMode,

    // Upload
    uploadMutation,
    fileInputRef,
    uploadPanelRef,
    isDragOverViewer,
    isDragOverSidebarUpload,
    handleViewerDragEnter,
    handleViewerDragOver,
    handleViewerDragLeave,
    handleViewerDrop,
    handleSidebarUploadDragEnter,
    handleSidebarUploadDragOver,
    handleSidebarUploadDragLeave,
    handleSidebarUploadDrop,
    handleOpenUploadArea,
    handleSidebarFileInputChange,

    // Sidebar
    panelHeightClass,
    isDesktopForPin,
    isDocsSidebarPinned,
    shouldUseHoverDocsSidebar,
    isDocsSidebarExpanded,
    handleDocsSidebarMouseEnter,
    handleDocsSidebarMouseLeave,
    handleToggleDocsSidebarPin,

    // Document list
    documentList,
    sortedDocuments,
    isListRefreshing,
    isDocumentListConnectivityError,
    handleRefresh,
    handleSelectDocument,

    // Document queries
    documentDetails,
    documentReview,
    processingHistory,
    visitScopingMetrics,

    // Derived document state
    isDocumentReviewed,
    isActiveDocumentProcessing,

    // Review split
    reviewSplitLayoutStyle,
    handleReviewSplitGridRef,
    resetReviewSplitRatio,
    startReviewSplitDragging,
    handleReviewSplitKeyboard,

    // Source panel
    sourcePanel,
    isPinnedSourcePanelVisible,

    // Raw text
    rawSearch,
    setRawSearch,
    rawSearchNotice,
    rawTextContent,
    hasRawText,
    canCopyRawText,
    isRawTextLoading,
    canSearchRawText,
    rawTextErrorMessage,
    handleRawSearch,
    copyFeedback,
    isCopyingRawText,
    handleDownloadRawText,
    handleCopyRawText,

    // Reprocessing
    reprocessMutation,
    reprocessingDocumentId,
    hasObservedProcessingAfterReprocess,
    showRetryModal,
    setShowRetryModal,
    handleConfirmRetry,

    // Review toggle
    reviewToggleMutation,
    toggleReviewStatus,

    // Structured data filters
    structuredSearchInput,
    setStructuredSearchInput,
    structuredSearchInputRef,
    selectedConfidenceBuckets,
    setSelectedConfidenceBuckets,
    activeConfidencePolicy,
    detectedFieldsSummary,
    showOnlyCritical,
    setShowOnlyCritical,
    showOnlyWithValue,
    setShowOnlyWithValue,
    showOnlyEmpty,
    setShowOnlyEmpty,
    getFilterToggleItemClass,
    resetStructuredFilters,

    // Review panel
    reviewPanelState,
    reviewPanelMessage,
    shouldShowReviewEmptyState,
    hasNoStructuredFilterResults,
    isRetryingInterpretation,
    handleRetryInterpretation,

    // Review data
    reportSections,
    renderSectionLayout,
    hasMalformedCanonicalFieldSlots,

    // Display constants
    reviewMessageInfoClass,
    reviewMessageMutedClass,
    reviewMessageWarningClass,
    shouldShowLoadPdfErrorBanner,
    loadPdfErrorMessage,
    processingHistoryErrorMessage,
    visitScopingErrorMessage,

    // DocumentsSidebar derived values
    isRefreshingDocuments,
    isDocumentListErrorVisible,
    documentListErrorMessage,

    // Selected field
    selectedReviewField,

    // Interpretation editing
    interpretationEditMutation,
    fieldEditing,

    // Feedback
    setUploadFeedback,
    setActionFeedback,

    // Utilities (passed to DocumentsSidebar)
    formatTimestamp,
    isProcessingTooLong,
    mapDocumentStatus,
    formatRunHeader,
    toggleStepDetails,
  };
}

// ---------------------------------------------------------------------------
// Provider + hook
// ---------------------------------------------------------------------------

type WorkspaceContextValue = ReturnType<typeof useWorkspaceValue>;

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const value = useWorkspaceValue();
  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useWorkspace(): WorkspaceContextValue {
  const ctx = useContext(WorkspaceContext);
  if (!ctx) throw new Error("useWorkspace must be used within WorkspaceProvider");
  return ctx;
}
