// Variant ownership by flow: uploads use success/error, action toasts use success/info/error.
export type UploadFeedback = {
  kind: "success" | "error";
  message: string;
  documentId?: string;
  showOpenAction?: boolean;
  technicalDetails?: string;
};

export type ActionFeedback = {
  kind: "success" | "error" | "info";
  message: string;
  technicalDetails?: string;
};

export type ConnectivityToast = Record<string, never>;
