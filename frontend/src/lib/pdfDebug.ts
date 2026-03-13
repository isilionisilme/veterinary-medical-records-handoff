export const PDF_ZOOM_STORAGE_KEY = "pdfViewerZoomLevel";
export const MIN_ZOOM_LEVEL = 0.5;
export const MAX_ZOOM_LEVEL = 2;
export const ZOOM_STEP = 0.1;

export type DebugFlags = {
  enabled: boolean;
  noTransformSubtree: boolean;
  noMotion: boolean;
  hardRemountCanvas: boolean;
};

export function clampZoomLevel(value: number): number {
  return Math.min(MAX_ZOOM_LEVEL, Math.max(MIN_ZOOM_LEVEL, value));
}

export function analyzeTransform(rawTransform: string): {
  determinant: number | null;
  negativeDeterminant: boolean;
  hasMirrorScale: boolean;
} {
  const transform = rawTransform.trim();
  if (transform === "none") {
    return {
      determinant: null,
      negativeDeterminant: false,
      hasMirrorScale: false,
    };
  }

  const scaleMirrorPattern = /scaleX\(\s*-|scale\(\s*-|matrix\(\s*-|matrix3d\(\s*-/i;
  const hasMirrorScale = scaleMirrorPattern.test(transform);

  const matrixMatch = transform.match(/^matrix\(([^)]+)\)$/i);
  if (matrixMatch) {
    const values = matrixMatch[1].split(",").map((value) => Number(value.trim()));
    if (values.length === 6 && values.every((value) => Number.isFinite(value))) {
      const [a, b, c, d] = values;
      const determinant = a * d - b * c;
      return {
        determinant,
        negativeDeterminant: determinant < 0,
        hasMirrorScale,
      };
    }
  }

  const matrix3dMatch = transform.match(/^matrix3d\(([^)]+)\)$/i);
  if (matrix3dMatch) {
    const values = matrix3dMatch[1].split(",").map((value) => Number(value.trim()));
    if (values.length === 16 && values.every((value) => Number.isFinite(value))) {
      const a = values[0];
      const b = values[1];
      const c = values[4];
      const d = values[5];
      const determinant = a * d - b * c;
      return {
        determinant,
        negativeDeterminant: determinant < 0,
        hasMirrorScale,
      };
    }
  }

  return {
    determinant: null,
    negativeDeterminant: false,
    hasMirrorScale,
  };
}

export function createDebugFlags(): DebugFlags {
  if (!import.meta.env.DEV || typeof window === "undefined") {
    return {
      enabled: false,
      noTransformSubtree: false,
      noMotion: false,
      hardRemountCanvas: false,
    };
  }

  const params = new URLSearchParams(window.location.search);
  const enabled = params.get("pdfDebug") === "1" || window.localStorage.getItem("pdfDebug") === "1";

  return {
    enabled,
    noTransformSubtree: enabled && params.get("pdfDebugNoTransform") === "1",
    noMotion: enabled && params.get("pdfDebugNoMotion") === "1",
    hardRemountCanvas: enabled && params.get("pdfDebugHardRemount") === "1",
  };
}

export function getNodeId(
  element: Element | null,
  nodeIdentityMap: WeakMap<Element, string>,
  nodeIdentityCounterRef: { current: number },
): string | null {
  if (!element) {
    return null;
  }
  let existing = nodeIdentityMap.get(element);
  if (!existing) {
    nodeIdentityCounterRef.current += 1;
    existing = `node-${nodeIdentityCounterRef.current}`;
    nodeIdentityMap.set(element, existing);
  }
  return existing;
}

type CaptureDebugSnapshotParams = {
  reason: string;
  pageIndex: number;
  canvas: HTMLCanvasElement;
  viewportScale: number;
  viewportRotation: number;
  renderTaskStatus: string;
  textLayerNodeId?: string | null;
  debugFlags: DebugFlags;
  nodeIdentityMap: WeakMap<Element, string>;
  nodeIdentityCounterRef: { current: number };
  lastCanvasNodeByPage: Map<number, string>;
  documentId: string | null;
  fileUrl: string | ArrayBuffer | null;
  filename?: string | null;
  pageNumber: number;
  zoomLevel: number;
  renderSession: number;
};

/* c8 ignore start -- dev-only PDF diagnostics not exercised in jsdom */
export function captureDebugSnapshot(params: CaptureDebugSnapshotParams): void {
  if (!params.debugFlags.enabled || typeof window === "undefined") {
    return;
  }

  const chain: Array<Record<string, unknown>> = [];
  let current: HTMLElement | null = params.canvas;
  for (let depth = 0; depth <= 6 && current; depth += 1) {
    const style = window.getComputedStyle(current);
    const transform = style.transform;
    const analysis = analyzeTransform(transform);
    chain.push({
      depth,
      nodeId: getNodeId(current, params.nodeIdentityMap, params.nodeIdentityCounterRef),
      tag: current.tagName,
      id: current.id || null,
      className: current.className || null,
      transform,
      transformOrigin: style.transformOrigin,
      direction: style.direction,
      writingMode: style.writingMode,
      scale: (style as CSSStyleDeclaration & { scale?: string }).scale ?? null,
      determinant: analysis.determinant,
      negativeDeterminant: analysis.negativeDeterminant,
      hasMirrorScale: analysis.hasMirrorScale,
      dirAttr: current.getAttribute("dir"),
    });
    current = current.parentElement;
  }

  const rect = params.canvas.getBoundingClientRect();
  const canvasNodeId = getNodeId(
    params.canvas,
    params.nodeIdentityMap,
    params.nodeIdentityCounterRef,
  );
  const previousCanvasNodeId = params.lastCanvasNodeByPage.get(params.pageIndex) ?? null;
  const canvasReused = previousCanvasNodeId === canvasNodeId;
  if (canvasNodeId) {
    params.lastCanvasNodeByPage.set(params.pageIndex, canvasNodeId);
  }

  const chainHasFlip = chain.some((entry) => {
    const negativeDeterminant = Boolean(entry.negativeDeterminant);
    const hasMirrorScale = Boolean(entry.hasMirrorScale);
    return negativeDeterminant || hasMirrorScale;
  });

  const snapshot = {
    timestamp: new Date().toISOString(),
    reason: params.reason,
    chainHasFlip,
    viewer: {
      documentId: params.documentId,
      fileUrl: typeof params.fileUrl === "string" ? params.fileUrl : "[array-buffer]",
      filename: params.filename,
      pageNumber: params.pageNumber,
      renderedPageIndex: params.pageIndex,
      zoomLevel: params.zoomLevel,
      viewportScale: params.viewportScale,
      viewportRotation: params.viewportRotation,
      appliedRotationState: 0,
      renderTaskStatus: params.renderTaskStatus,
      renderSession: params.renderSession,
    },
    runtime: {
      devicePixelRatio: window.devicePixelRatio,
    },
    canvas: {
      nodeId: canvasNodeId,
      reused: canvasReused,
      previousNodeId: previousCanvasNodeId,
      attrWidth: params.canvas.width,
      attrHeight: params.canvas.height,
      styleWidth: params.canvas.style.width || null,
      styleHeight: params.canvas.style.height || null,
      computedTransform: window.getComputedStyle(params.canvas).transform,
      rect: {
        x: rect.x,
        y: rect.y,
        width: rect.width,
        height: rect.height,
      },
    },
    layers: {
      textLayerNodeId: params.textLayerNodeId ?? null,
      textLayerReused: false,
    },
    chain,
  };

  const debugWindow = window as Window & {
    __pdfBugSnapshots?: Array<Record<string, unknown>>;
  };
  const store = debugWindow.__pdfBugSnapshots ?? [];
  store.push(snapshot as unknown as Record<string, unknown>);
  if (store.length > 200) {
    store.shift();
  }
  debugWindow.__pdfBugSnapshots = store;

  console.groupCollapsed(
    `[PdfBugSnapshot] ${params.reason} | doc=${params.documentId ?? "unknown"} page=${params.pageIndex}`,
  );
  console.log(snapshot);
  console.groupEnd();
}
/* c8 ignore stop */
