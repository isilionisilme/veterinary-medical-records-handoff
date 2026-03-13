import { useCallback, useEffect, useRef, useState } from "react";

import { type ConnectivityToast } from "../components/toast/toast-types";

export function useConnectivityToasts() {
  const [connectivityToast, setConnectivityToast] = useState<ConnectivityToast | null>(null);
  const [hasShownListErrorToast, setHasShownListErrorToast] = useState(false);
  const lastConnectivityToastAtRef = useRef(0);

  useEffect(() => {
    if (!connectivityToast) {
      return;
    }
    const timer = window.setTimeout(() => setConnectivityToast(null), 5000);
    return () => window.clearTimeout(timer);
  }, [connectivityToast]);

  const showConnectivityToast = useCallback(() => {
    const now = Date.now();
    if (now - lastConnectivityToastAtRef.current < 5000) {
      return;
    }
    lastConnectivityToastAtRef.current = now;
    setConnectivityToast({});
  }, []);

  return {
    connectivityToast,
    showConnectivityToast,
    setConnectivityToast,
    hasShownListErrorToast,
    setHasShownListErrorToast,
  };
}
