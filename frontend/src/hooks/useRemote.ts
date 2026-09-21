import { useEffect, useState } from "react";
import { apiFetch } from "../services/api";
export function useRemote<T>(path: string, revision = 0) {
  const [state, setState] = useState<{
    path: string;
    data?: T;
    error?: string;
    loading: boolean;
  }>({ path: "", loading: true });
  useEffect(() => {
    const controller = new AbortController();
    apiFetch<T>(path, { signal: controller.signal })
      .then((data) => {
        if (!controller.signal.aborted)
          setState({ path, data, loading: false });
      })
      .catch((e: Error) => {
        if (!controller.signal.aborted)
          setState({ path, error: e.message, loading: false });
      });
    return () => controller.abort();
  }, [path, revision]);
  return state.path === path
    ? state
    : { loading: true, data: undefined, error: undefined };
}
