import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { DocumentsSidebar } from "./components/DocumentsSidebar";
import { buildViewerToolbarContent } from "./components/viewer/viewerToolbarContent";
import { PdfViewerPanel } from "./components/workspace/PdfViewerPanel";
import { StructuredDataPanel } from "./components/workspace/StructuredDataPanel";
import { ToastHost } from "./components/toast/ToastHost";
import { SourcePanelContent } from "./components/review/SourcePanelContent";
import { WorkspaceDialogs } from "./components/review/WorkspaceDialogs";
import { type ActionFeedback, type UploadFeedback } from "./components/toast/toast-types";
import { useConnectivityToasts } from "./hooks/useConnectivityToasts";
import { useFieldEditing } from "./hooks/useFieldEditing";
import { useClinicAddressLookup } from "./hooks/useClinicAddressLookup";
import { useDocumentsSidebar } from "./hooks/useDocumentsSidebar";
import { useReviewSplitPanel } from "./hooks/useReviewSplitPanel";
import { useStructuredDataFilters } from "./hooks/useStructuredDataFilters";
import { useSourcePanelState } from "./hooks/useSourcePanelState";
import { useUploadState } from "./hooks/useUploadState";
import { useReviewedEditBlocker } from "./hooks/useReviewedEditBlocker";
import { useDocumentLoader } from "./hooks/useDocumentLoader";
import { useReprocessing } from "./hooks/useReprocessing";
import { useReviewToggle } from "./hooks/useReviewToggle";
import { useInterpretationEdit } from "./hooks/useInterpretationEdit";
import { useDocumentUpload } from "./hooks/useDocumentUpload";
import { useDocumentListPolling } from "./hooks/useDocumentListPolling";
import { useRawTextViewer } from "./hooks/useRawTextViewer";
import { useConfidenceDiagnostics } from "./hooks/useConfidenceDiagnostics";
import { useReviewDataPipeline } from "./hooks/useReviewDataPipeline";
import { useReviewPanelStatus } from "./hooks/useReviewPanelStatus";
import { useActiveDocumentQueries } from "./hooks/useActiveDocumentQueries";
import { useReviewRenderers } from "./hooks/useReviewRenderers";
import {
  API_BASE_URL,
  MAX_UPLOAD_SIZE_BYTES,
  REVIEW_MESSAGE_INFO_CLASS,
  REVIEW_MESSAGE_MUTED_CLASS,
  REVIEW_MESSAGE_WARNING_CLASS,
} from "./constants/appWorkspace";
import {
  formatRunHeader,
  formatTimestamp,
  getTechnicalDetails,
  getUserErrorMessage,
  isConnectivityOrServerError,
  isDocumentProcessing,
  isProcessingTooLong,
} from "./lib/appWorkspaceUtils";
import { mapDocumentStatus } from "./lib/documentStatus";
import { type ReviewSelectableField, type ReviewVisitGroup } from "./types/appWorkspace";
export {
  MIN_PDF_PANEL_WIDTH_PX,
  REVIEW_SPLIT_MIN_WIDTH_PX,
  SPLITTER_COLUMN_WIDTH_PX,
} from "./constants/appWorkspace";
export function App() {
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
  const {
    connectivityToast,
    showConnectivityToast,
    setConnectivityToast,
    hasShownListErrorToast,
    setHasShownListErrorToast,
  } = useConnectivityToasts();
  const { fileUrl, filename, requestPdfLoad, loadPdf, pendingAutoOpenDocumentIdRef } =
    useDocumentLoader({
      onUploadFeedback: setUploadFeedback,
    });
  const effectiveViewMode = "browse";
  const isReviewMode = false;
  const isBrowseMode = true;
  const downloadUrl = useMemo(() => {
    if (!activeId) {
      return null;
    }
    return `${API_BASE_URL}/documents/${activeId}/download?download=true`;
  }, [activeId]);
  useEffect(() => {
    return () => {
      const refreshTimer = refreshFeedbackTimerRef.current;
      if (refreshTimer) {
        window.clearTimeout(refreshTimer);
      }
    };
  }, []);
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
  const sourcePanel = useSourcePanelState({
    isDesktopForPin,
    onNotice: setEvidenceNotice,
  });
  const handleSelectDocument = (docId: string) => {
    setActiveId(docId);
    requestPdfLoad(docId);
  };
  useEffect(() => {
    if (activeViewerTab !== "document" || !activeId || fileUrl) {
      return;
    }
    requestPdfLoad(activeId);
  }, [activeViewerTab, activeId, fileUrl, requestPdfLoad]);
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
  const resetSourcePanel = sourcePanel.reset;
  useEffect(() => {
    setSelectedFieldId(null);
    setFieldNavigationRequestId(0);
    setEvidenceNotice(null);
    setExpandedFieldValues({});
    resetSourcePanel();
  }, [activeId, resetSourcePanel]);
  const { interpretationEditMutation, submitInterpretationChanges } = useInterpretationEdit({
    activeId,
    reviewPayload: documentReview.data,
    onActionFeedback: setActionFeedback,
  });
  const panelHeightClass = "h-[clamp(720px,88vh,980px)]";
  const toggleStepDetails = (key: string) => {
    setExpandedSteps((prev) => ({ ...prev, [key]: !prev[key] }));
  };
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
  const { reviewToggleMutation } = useReviewToggle({
    onActionFeedback: setActionFeedback,
  });
  useEffect(() => {
    if (!uploadFeedback) {
      return;
    }
    const timeoutMs = uploadFeedback.kind === "success" ? 3500 : 5000;
    const timer = window.setTimeout(() => setUploadFeedback(null), timeoutMs);
    return () => window.clearTimeout(timer);
  }, [uploadFeedback]);
  useEffect(() => {
    if (!actionFeedback) {
      return;
    }
    const timeoutMs = actionFeedback.kind === "success" ? 3500 : 5000;
    const timer = window.setTimeout(() => setActionFeedback(null), timeoutMs);
    return () => window.clearTimeout(timer);
  }, [actionFeedback]);
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
  }, [documentList.isError, documentList.isSuccess, documentList.error, hasShownListErrorToast]);
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
  ]);
  useEffect(() => {
    if (!loadPdf.isError || !isConnectivityOrServerError(loadPdf.error)) {
      return;
    }
    showConnectivityToast();
  }, [loadPdf.error, loadPdf.failureCount, loadPdf.isError]);
  const interpretationData = documentReview.data?.active_interpretation.data;
  const schemaContract =
    typeof interpretationData?.schema_contract === "string"
      ? interpretationData.schema_contract.trim().toLowerCase()
      : null;
  const hasCanonicalContractSignal = schemaContract === "visit-grouped-canonical";
  const localIsCanonicalContract = hasCanonicalContractSignal;
  const localHasMalformedCanonicalFieldSlots = useMemo(() => {
    if (!localIsCanonicalContract) {
      return false;
    }
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
  const { activeConfidencePolicy } = useConfidenceDiagnostics({
    interpretationData,
    reviewVisits: localReviewVisits,
    isCanonicalContract: localIsCanonicalContract,
  });
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
  const selectedReviewField = useMemo(() => {
    if (!selectedFieldId) {
      return null;
    }
    return selectableReviewItems.find((field) => field.id === selectedFieldId) ?? null;
  }, [selectableReviewItems, selectedFieldId]);
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
  const reviewMessageInfoClass = REVIEW_MESSAGE_INFO_CLASS;
  const reviewMessageMutedClass = REVIEW_MESSAGE_MUTED_CLASS;
  const reviewMessageWarningClass = REVIEW_MESSAGE_WARNING_CLASS;
  const shouldShowLoadPdfErrorBanner =
    loadPdf.isError && !isConnectivityOrServerError(loadPdf.error);
  const isPinnedSourcePanelVisible =
    isBrowseMode && sourcePanel.isSourceOpen && sourcePanel.isSourcePinned && isDesktopForPin;
  const isDocumentListConnectivityError =
    documentList.isError && isConnectivityOrServerError(documentList.error);
  const handleSelectReviewItem = useCallback((field: ReviewSelectableField) => {
    setSelectedFieldId(field.id);
    setFieldNavigationRequestId((current) => current + 1);
  }, []);
  const { handleReviewedEditAttempt, handleReviewedKeyboardEditAttempt } = useReviewedEditBlocker({
    isDocumentReviewed,
    onActionFeedback: setActionFeedback,
  });
  useEffect(() => {
    if (!selectedFieldId) {
      return;
    }
    const currentIds = new Set(selectableReviewItems.map((field) => field.id));
    if (!currentIds.has(selectedFieldId)) {
      setSelectedFieldId(null);
    }
  }, [selectableReviewItems, selectedFieldId]);
  useEffect(() => {
    if (!evidenceNotice) {
      return;
    }
    const timer = window.setTimeout(() => setEvidenceNotice(null), 3000);
    return () => window.clearTimeout(timer);
  }, [evidenceNotice]);
  const { toolbarLeftContent: viewerModeToolbarIcons, toolbarRightExtra: viewerDownloadIcon } =
    buildViewerToolbarContent({
      activeViewerTab,
      onChangeTab: setActiveViewerTab,
      downloadUrl,
    });
  const {
    editingField,
    editingFieldDraftValue,
    setEditingFieldDraftValue,
    isAddFieldDialogOpen,
    addFieldKeyDraft,
    setAddFieldKeyDraft,
    addFieldValueDraft,
    setAddFieldValueDraft,
    openFieldEditDialog,
    closeFieldEditDialog,
    saveFieldEditDialog,
    closeAddFieldDialog,
    saveAddFieldDialog,
    editingFieldCandidateSections,
    isEditingMicrochipField,
    isEditingMicrochipInvalid,
    isEditingWeightField,
    isEditingWeightInvalid,
    isEditingAgeField,
    isEditingAgeInvalid,
    isEditingDateField,
    isEditingDateInvalid,
    isEditingSexField,
    isEditingSexInvalid,
    isEditingSpeciesField,
    isEditingSpeciesInvalid,
  } = useFieldEditing({
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
        if (clinicAddressField) {
          startLookup(clinicNameValue, clinicAddressField);
        }
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
  const { renderSectionLayout } = useReviewRenderers({
    activeConfidencePolicy,
    isDocumentReviewed,
    isInterpretationEditPending: interpretationEditMutation.isPending,
    selectedFieldId,
    expandedFieldValues,
    hoveredFieldTriggerId,
    hoveredCriticalTriggerId,
    hasUnassignedVisitGroup,
    onOpenFieldEditDialog: openFieldEditDialog,
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
  const sourcePanelContent = (
    <SourcePanelContent
      sourcePage={sourcePanel.sourcePage}
      sourceSnippet={sourcePanel.sourceSnippet}
      isSourcePinned={sourcePanel.isSourcePinned}
      isDesktopForPin={isDesktopForPin}
      onTogglePin={sourcePanel.togglePin}
      onClose={sourcePanel.closeOverlay}
      fileUrl={fileUrl}
      activeId={activeId}
      filename={filename}
      focusRequestId={sourcePanel.focusRequestId}
    />
  );
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
  const structuredDataPanel = (
    <StructuredDataPanel
      activeId={activeId}
      isActiveDocumentProcessing={isActiveDocumentProcessing}
      isDocumentReviewed={isDocumentReviewed}
      reviewTogglePending={reviewToggleMutation.isPending}
      onToggleReviewStatus={() => {
        if (!activeId) {
          return;
        }
        reviewToggleMutation.mutate({
          docId: activeId,
          target: isDocumentReviewed ? "in_review" : "reviewed",
        });
      }}
      reviewPanelState={reviewPanelState}
      structuredSearchInput={structuredSearchInput}
      structuredSearchInputRef={
        structuredSearchInputRef as import("react").RefObject<HTMLInputElement>
      }
      setStructuredSearchInput={setStructuredSearchInput}
      selectedConfidenceBuckets={selectedConfidenceBuckets}
      setSelectedConfidenceBuckets={setSelectedConfidenceBuckets}
      activeConfidencePolicy={activeConfidencePolicy}
      detectedFieldsSummary={detectedFieldsSummary}
      showOnlyCritical={showOnlyCritical}
      showOnlyWithValue={showOnlyWithValue}
      showOnlyEmpty={showOnlyEmpty}
      setShowOnlyCritical={setShowOnlyCritical}
      setShowOnlyWithValue={setShowOnlyWithValue}
      setShowOnlyEmpty={setShowOnlyEmpty}
      getFilterToggleItemClass={getFilterToggleItemClass}
      resetStructuredFilters={resetStructuredFilters}
      reviewMessageInfoClass={reviewMessageInfoClass}
      reviewMessageMutedClass={reviewMessageMutedClass}
      reviewMessageWarningClass={reviewMessageWarningClass}
      reviewPanelMessage={reviewPanelMessage}
      shouldShowReviewEmptyState={shouldShowReviewEmptyState}
      isRetryingInterpretation={isRetryingInterpretation}
      onRetryInterpretation={handleRetryInterpretation}
      hasMalformedCanonicalFieldSlots={hasMalformedCanonicalFieldSlots}
      hasNoStructuredFilterResults={hasNoStructuredFilterResults}
      reportSections={reportSections}
      renderSectionLayout={renderSectionLayout}
      evidenceNotice={evidenceNotice}
    />
  );
  return (
    <div className="min-h-screen bg-page px-4 py-3 md:px-6 lg:px-8 xl:px-10">
      <WorkspaceDialogs
        isInterpretationEditPending={interpretationEditMutation.isPending}
        isAddFieldDialogOpen={isAddFieldDialogOpen}
        addFieldKeyDraft={addFieldKeyDraft}
        addFieldValueDraft={addFieldValueDraft}
        onFieldKeyChange={setAddFieldKeyDraft}
        onFieldValueChange={setAddFieldValueDraft}
        onCloseAddFieldDialog={closeAddFieldDialog}
        onSaveAddFieldDialog={saveAddFieldDialog}
        editingField={editingField}
        editingFieldDraftValue={editingFieldDraftValue}
        onEditingFieldDraftValueChange={setEditingFieldDraftValue}
        editingFieldCandidateSections={editingFieldCandidateSections}
        isEditingMicrochipField={isEditingMicrochipField}
        isEditingMicrochipInvalid={isEditingMicrochipInvalid}
        isEditingWeightField={isEditingWeightField}
        isEditingWeightInvalid={isEditingWeightInvalid}
        isEditingAgeField={isEditingAgeField}
        isEditingAgeInvalid={isEditingAgeInvalid}
        isEditingDateField={isEditingDateField}
        isEditingDateInvalid={isEditingDateInvalid}
        isEditingSexField={isEditingSexField}
        isEditingSexInvalid={isEditingSexInvalid}
        isEditingSpeciesField={isEditingSpeciesField}
        isEditingSpeciesInvalid={isEditingSpeciesInvalid}
        onCloseFieldEditDialog={closeFieldEditDialog}
        onSaveFieldEditDialog={saveFieldEditDialog}
      />
      <div
        className="mx-auto w-full max-w-[1640px] rounded-frame bg-canvas p-[var(--canvas-gap)]"
        data-testid="canvas-wrapper"
      >
        <main className="relative w-full">
          <div
            className="relative z-20 flex gap-[var(--canvas-gap)]"
            data-testid="main-canvas-layout"
          >
            <DocumentsSidebar
              panelHeightClass={panelHeightClass}
              shouldUseHoverDocsSidebar={shouldUseHoverDocsSidebar}
              isDocsSidebarExpanded={isDocsSidebarExpanded}
              isDocsSidebarPinned={isDocsSidebarPinned}
              isRefreshingDocuments={documentList.isFetching || showRefreshFeedback}
              isUploadPending={uploadMutation.isPending}
              isDragOverSidebarUpload={isDragOverSidebarUpload}
              isDocumentListLoading={documentList.isLoading}
              isDocumentListError={documentList.isError && !isDocumentListConnectivityError}
              isListRefreshing={isListRefreshing}
              documentListErrorMessage={
                documentList.isError && !isDocumentListConnectivityError
                  ? getUserErrorMessage(documentList.error, "No se pudieron cargar los documentos.")
                  : null
              }
              documents={sortedDocuments}
              activeId={activeId}
              uploadPanelRef={uploadPanelRef}
              fileInputRef={fileInputRef}
              formatTimestamp={formatTimestamp}
              isProcessingTooLong={isProcessingTooLong}
              mapDocumentStatus={mapDocumentStatus}
              onSidebarMouseEnter={handleDocsSidebarMouseEnter}
              onSidebarMouseLeave={handleDocsSidebarMouseLeave}
              onTogglePin={handleToggleDocsSidebarPin}
              onRefresh={handleRefresh}
              onOpenUploadArea={handleOpenUploadArea}
              onSidebarUploadDragEnter={handleSidebarUploadDragEnter}
              onSidebarUploadDragOver={handleSidebarUploadDragOver}
              onSidebarUploadDragLeave={handleSidebarUploadDragLeave}
              onSidebarUploadDrop={handleSidebarUploadDrop}
              onSidebarFileInputChange={handleSidebarFileInputChange}
              onSelectDocument={handleSelectDocument}
            />
            <section className={`flex min-w-0 flex-1 flex-col ${panelHeightClass}`}>
              <PdfViewerPanel
                activeViewerTab={activeViewerTab}
                activeId={activeId}
                fileUrl={fileUrl}
                filename={filename}
                isDragOverViewer={isDragOverViewer}
                onViewerDragEnter={handleViewerDragEnter}
                onViewerDragOver={handleViewerDragOver}
                onViewerDragLeave={handleViewerDragLeave}
                onViewerDrop={handleViewerDrop}
                onOpenUploadArea={handleOpenUploadArea}
                isDocumentListError={documentList.isError}
                shouldShowLoadPdfErrorBanner={shouldShowLoadPdfErrorBanner}
                loadPdfErrorMessage={loadPdfErrorMessage}
                reviewSplitLayoutStyle={reviewSplitLayoutStyle}
                onReviewSplitGridRef={handleReviewSplitGridRef}
                onStartReviewSplitDragging={startReviewSplitDragging}
                onResetReviewSplitRatio={resetReviewSplitRatio}
                onHandleReviewSplitKeyboard={handleReviewSplitKeyboard}
                effectiveViewMode={effectiveViewMode}
                selectedReviewFieldEvidencePage={selectedReviewField?.evidence?.page ?? null}
                selectedReviewFieldEvidenceSnippet={selectedReviewField?.evidence?.snippet ?? null}
                fieldNavigationRequestId={fieldNavigationRequestId}
                viewerModeToolbarIcons={viewerModeToolbarIcons}
                viewerDownloadIcon={viewerDownloadIcon}
                structuredDataPanel={structuredDataPanel}
                isPinnedSourcePanelVisible={isPinnedSourcePanelVisible}
                sourcePanelContent={sourcePanelContent}
                isSourceOpen={sourcePanel.isSourceOpen}
                isSourcePinned={sourcePanel.isSourcePinned}
                isDesktopForPin={isDesktopForPin}
                isReviewMode={isReviewMode}
                onCloseSourceOverlay={sourcePanel.closeOverlay}
                rawSearch={rawSearch}
                setRawSearch={setRawSearch}
                canSearchRawText={canSearchRawText}
                hasRawText={hasRawText}
                rawSearchNotice={rawSearchNotice}
                isRawTextLoading={isRawTextLoading}
                rawTextErrorMessage={rawTextErrorMessage}
                rawTextContent={rawTextContent ?? ""}
                onRawSearch={handleRawSearch}
                canCopyRawText={canCopyRawText}
                isCopyingRawText={isCopyingRawText}
                copyFeedback={copyFeedback}
                onCopyRawText={handleCopyRawText}
                onDownloadRawText={handleDownloadRawText}
                isActiveDocumentProcessing={isActiveDocumentProcessing}
                reprocessPending={reprocessMutation.isPending}
                reprocessingDocumentId={reprocessingDocumentId}
                hasObservedProcessingAfterReprocess={hasObservedProcessingAfterReprocess}
                onOpenRetryModal={() => setShowRetryModal(true)}
                showRetryModal={showRetryModal}
                onShowRetryModalChange={setShowRetryModal}
                onConfirmRetry={handleConfirmRetry}
                processingHistoryIsLoading={processingHistory.isLoading}
                processingHistoryIsError={processingHistory.isError}
                processingHistoryErrorMessage={processingHistoryErrorMessage}
                processingHistoryRuns={processingHistory.data?.runs ?? []}
                visitScopingMetrics={visitScopingMetrics.data ?? null}
                visitScopingIsLoading={visitScopingMetrics.isLoading}
                visitScopingIsError={visitScopingMetrics.isError}
                visitScopingErrorMessage={visitScopingErrorMessage}
                expandedSteps={expandedSteps}
                onToggleStepDetails={toggleStepDetails}
                formatRunHeader={formatRunHeader}
              />
            </section>
          </div>
        </main>
        <ToastHost
          connectivityToast={connectivityToast}
          uploadFeedback={uploadFeedback}
          actionFeedback={actionFeedback}
          onCloseConnectivityToast={() => setConnectivityToast(null)}
          onCloseUploadFeedback={() => setUploadFeedback(null)}
          onCloseActionFeedback={() => setActionFeedback(null)}
          onOpenUploadedDocument={(documentId) => {
            setActiveViewerTab("document");
            setActiveId(documentId);
            requestPdfLoad(documentId);
            setUploadFeedback(null);
          }}
        />
      </div>
    </div>
  );
}
