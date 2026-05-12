import { useState } from "react";
import { importPadron } from "../services/padron.service";

export default function Padron() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setError("Seleccioná un archivo Excel.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      const data = await importPadron(file);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Error al importar padrón.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="font-heading text-3xl font-bold text-foreground">
          Importar padrón
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Subí el Excel del padrón de afiliados del Partido Justicialista.
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-lg border bg-card p-6 shadow-sm"
      >
        <input
          type="file"
          accept=".xlsx,.xls"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="block w-full rounded-md border bg-background px-3 py-2 text-sm"
        />

        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90 disabled:opacity-60"
        >
          {loading ? "Importando..." : "Importar padrón"}
        </button>

        {error && (
          <div className="rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
            {error}
          </div>
        )}
      </form>

      {result && (
        <div className="rounded-lg border bg-card p-6 shadow-sm">
          <h2 className="font-heading text-xl font-semibold">Resultado</h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-md border p-4">
              <p className="text-sm text-muted-foreground">Archivo</p>
              <p className="font-medium">{result.file_name}</p>
            </div>
            <div className="rounded-md border p-4">
              <p className="text-sm text-muted-foreground">Total filas</p>
              <p className="font-medium">{result.total_rows}</p>
            </div>
            <div className="rounded-md border p-4">
              <p className="text-sm text-muted-foreground">Válidas</p>
              <p className="font-medium">{result.valid_rows}</p>
            </div>
            <div className="rounded-md border p-4">
              <p className="text-sm text-muted-foreground">Inválidas</p>
              <p className="font-medium">{result.invalid_rows}</p>
            </div>
            <div className="rounded-md border p-4">
              <p className="text-sm text-muted-foreground">Estado</p>
              <p className="font-medium">{result.status}</p>
            </div>
            <div className="rounded-md border p-4">
              <p className="text-sm text-muted-foreground">Batch ID</p>
              <p className="font-medium">{result.batch_id}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}