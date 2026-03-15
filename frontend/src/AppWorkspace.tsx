import { DocumentsSidebar } from "./components/DocumentsSidebar";
import { SourcePanelContent } from "./components/review/SourcePanelContent";
import { WorkspaceDialogs } from "./components/review/WorkspaceDialogs";
import { ToastHost } from "./components/toast/ToastHost";
import { buildViewerToolbarContent } from "./components/viewer/viewerToolbarContent";
import { PdfViewerPanel } from "./components/workspace/PdfViewerPanel";
import { StructuredDataPanel } from "./components/workspace/StructuredDataPanel";
import { useWorkspace, WorkspaceProvider } from "./context/WorkspaceContext";
export {
  MIN_PDF_PANEL_WIDTH_PX,
  REVIEW_SPLIT_MIN_WIDTH_PX,
  SPLITTER_COLUMN_WIDTH_PX,
} from "./constants/appWorkspace";
export function App() {
  return (
    <WorkspaceProvider>
      <WorkspaceLayout />
    </WorkspaceProvider>
  );
}

function WorkspaceLayout() {
  const ws = useWorkspace();

  const { toolbarLeftContent: viewerModeToolbarIcons, toolbarRightExtra: viewerDownloadIcon } =
    buildViewerToolbarContent({
      activeViewerTab: ws.activeViewerTab,
      onChangeTab: ws.setActiveViewerTab,
      downloadUrl: ws.downloadUrl,
    });

  const sourcePanelContent = (
    <SourcePanelContent
      sourcePage={ws.sourcePanel.sourcePage}
      sourceSnippet={ws.sourcePanel.sourceSnippet}
      isSourcePinned={ws.sourcePanel.isSourcePinned}
      isDesktopForPin={ws.isDesktopForPin}
      onTogglePin={ws.sourcePanel.togglePin}
      onClose={ws.sourcePanel.closeOverlay}
      fileUrl={ws.fileUrl}
      activeId={ws.activeId}
      filename={ws.filename}
      focusRequestId={ws.sourcePanel.focusRequestId}
    />
  );

  const structuredDataPanel = <StructuredDataPanel />;

  return (
    <div className="min-h-screen bg-page px-4 py-3 md:px-6 lg:px-8 xl:px-10">
      <WorkspaceDialogs
        isInterpretationEditPending={ws.interpretationEditMutation.isPending}
        isAddFieldDialogOpen={ws.fieldEditing.isAddFieldDialogOpen}
        addFieldKeyDraft={ws.fieldEditing.addFieldKeyDraft}
        addFieldValueDraft={ws.fieldEditing.addFieldValueDraft}
        onFieldKeyChange={ws.fieldEditing.setAddFieldKeyDraft}
        onFieldValueChange={ws.fieldEditing.setAddFieldValueDraft}
        onCloseAddFieldDialog={ws.fieldEditing.closeAddFieldDialog}
        onSaveAddFieldDialog={ws.fieldEditing.saveAddFieldDialog}
        editingField={ws.fieldEditing.editingField}
        editingFieldDraftValue={ws.fieldEditing.editingFieldDraftValue}
        onEditingFieldDraftValueChange={ws.fieldEditing.setEditingFieldDraftValue}
        editingFieldCandidateSections={ws.fieldEditing.editingFieldCandidateSections}
        isEditingMicrochipField={ws.fieldEditing.isEditingMicrochipField}
        isEditingMicrochipInvalid={ws.fieldEditing.isEditingMicrochipInvalid}
        isEditingWeightField={ws.fieldEditing.isEditingWeightField}
        isEditingWeightInvalid={ws.fieldEditing.isEditingWeightInvalid}
        isEditingAgeField={ws.fieldEditing.isEditingAgeField}
        isEditingAgeInvalid={ws.fieldEditing.isEditingAgeInvalid}
        isEditingDateField={ws.fieldEditing.isEditingDateField}
        isEditingDateInvalid={ws.fieldEditing.isEditingDateInvalid}
        isEditingSexField={ws.fieldEditing.isEditingSexField}
        isEditingSexInvalid={ws.fieldEditing.isEditingSexInvalid}
        isEditingSpeciesField={ws.fieldEditing.isEditingSpeciesField}
        isEditingSpeciesInvalid={ws.fieldEditing.isEditingSpeciesInvalid}
        onCloseFieldEditDialog={ws.fieldEditing.closeFieldEditDialog}
        onSaveFieldEditDialog={ws.fieldEditing.saveFieldEditDialog}
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
            <DocumentsSidebar />
            <section className={`flex min-w-0 flex-1 flex-col ${ws.panelHeightClass}`}>
              <PdfViewerPanel
                structuredDataPanel={structuredDataPanel}
                sourcePanelContent={sourcePanelContent}
                viewerModeToolbarIcons={viewerModeToolbarIcons}
                viewerDownloadIcon={viewerDownloadIcon}
              />
            </section>
          </div>
        </main>
        <ToastHost
          connectivityToast={ws.connectivityToast}
          uploadFeedback={ws.uploadFeedback}
          actionFeedback={ws.actionFeedback}
          onCloseConnectivityToast={() => ws.setConnectivityToast(null)}
          onCloseUploadFeedback={() => ws.setUploadFeedback(null)}
          onCloseActionFeedback={() => ws.setActionFeedback(null)}
          onOpenUploadedDocument={(documentId) => {
            ws.setActiveViewerTab("document");
            ws.handleSelectDocument(documentId);
            ws.setUploadFeedback(null);
          }}
        />
      </div>
    </div>
  );
}
