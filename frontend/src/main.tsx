import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";

function App() {
  return (
    <div className="min-h-screen bg-background text-foreground font-body">
      <main className="mx-auto flex min-h-screen max-w-7xl items-center justify-center p-6">
        <div className="w-full max-w-xl rounded-lg border bg-card p-8 text-center shadow-sm">
          <span className="inline-flex rounded-full bg-primary px-3 py-1 text-sm font-medium text-primary-foreground">
            Junta Electoral
          </span>

          <h1 className="mt-6 font-heading text-4xl font-bold tracking-tight text-foreground">
            Plataforma PJ Candidatos
          </h1>

          <p className="mt-3 text-muted-foreground">
            Frontend inicial configurado con React, TypeScript, Tailwind y base
            visual alineada al mockup.
          </p>

          <div className="mt-8 grid gap-3 sm:grid-cols-2">
            <div className="rounded-md border bg-muted/40 p-4">
              <p className="font-medium text-foreground">Estado</p>
              <p className="text-sm text-muted-foreground">
                Configuración inicial lista
              </p>
            </div>

            <div className="rounded-md border bg-muted/40 p-4">
              <p className="font-medium text-foreground">Siguiente paso</p>
              <p className="text-sm text-muted-foreground">
                Router + layout + login
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);