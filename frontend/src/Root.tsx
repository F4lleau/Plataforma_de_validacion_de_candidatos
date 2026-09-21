import { useEffect } from "react";
import App from "./App";
import { useAuthStore } from "./stores/auth.store";

export default function Root() {
  const restoreSession = useAuthStore((state) => state.restoreSession);

  useEffect(() => {
    void restoreSession();
  }, [restoreSession]);

  return <App />;
}
