import { useEffect } from "react";
import App from "./App";
import { useAuthStore } from "./stores/auth.store";

export default function Root() {
  const restoreSession = useAuthStore((state) => state.restoreSession);

  useEffect(() => {
    void restoreSession();
    const syncSession = (event: StorageEvent) => {
      if (event.key === "access_token" || event.key === null) void restoreSession();
    };
    window.addEventListener("storage", syncSession);
    return () => window.removeEventListener("storage", syncSession);
  }, [restoreSession]);

  return <App />;
}
