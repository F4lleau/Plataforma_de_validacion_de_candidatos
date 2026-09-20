import { useState } from "react";
import {
  createCandidate,
  type CandidateCreatePayload,
} from "../services/candidates.service";

export default function Candidatos() {
  const [form, setForm] = useState({
    dni: "",
    first_name: "",
    last_name: "",
    birth_date: "",
    gender: "",
    cargo_label: "",
    office_id: "",
    election_id: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [warning, setWarning] = useState("");

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");
    setWarning("");

    const payload: CandidateCreatePayload = {
      person: {
        dni: form.dni,
        first_name: form.first_name,
        last_name: form.last_name,
        birth_date: form.birth_date,
        gender: form.gender,
      },
      office_id: Number(form.office_id),
      election_id: Number(form.election_id),
    };

    try {
      const result = await createCandidate(payload);
      if (result.affiliation.status === "warning") {
        setWarning(
          "El candidato fue registrado, pero no figura en el padrón de afiliados vigente. Quedará pendiente de revisión por la Junta Electoral.",
        );
      } else {
        setSuccess(
          "El candidato fue registrado y su afiliación fue verificada.",
        );
      }
    } catch (err: unknown) {
      setError(
        err instanceof Error ? err.message : "Error al guardar candidato.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="font-heading text-3xl font-bold text-foreground">
          Cargar candidato
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Alta manual de candidato para una lista.
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="grid gap-4 rounded-lg border bg-card p-6 shadow-sm md:grid-cols-2"
      >
        <input
          name="dni"
          placeholder="DNI"
          value={form.dni}
          onChange={handleChange}
          className="rounded-md border px-3 py-2 text-sm"
        />
        <input
          name="first_name"
          placeholder="Nombre"
          value={form.first_name}
          onChange={handleChange}
          className="rounded-md border px-3 py-2 text-sm"
        />
        <input
          name="last_name"
          placeholder="Apellido"
          value={form.last_name}
          onChange={handleChange}
          className="rounded-md border px-3 py-2 text-sm"
        />
        <input
          name="birth_date"
          type="date"
          value={form.birth_date}
          onChange={handleChange}
          className="rounded-md border px-3 py-2 text-sm"
        />
        <select
          name="gender"
          value={form.gender}
          onChange={handleChange}
          className="rounded-md border px-3 py-2 text-sm"
        >
          <option value="">Seleccionar sexo</option>
          <option value="M">Masculino</option>
          <option value="F">Femenino</option>
        </select>
        <input
          name="cargo_label"
          placeholder="Cargo en la lista"
          value={form.cargo_label}
          onChange={handleChange}
          className="rounded-md border px-3 py-2 text-sm"
        />
        <input
          name="office_id"
          type="number"
          min="1"
          placeholder="ID del cargo"
          value={form.office_id}
          onChange={handleChange}
          required
          className="rounded-md border px-3 py-2 text-sm"
        />
        <input
          name="election_id"
          type="number"
          min="1"
          placeholder="ID de elección"
          value={form.election_id}
          onChange={handleChange}
          required
          className="rounded-md border px-3 py-2 text-sm"
        />

        <div className="md:col-span-2">
          <button
            type="submit"
            disabled={loading}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90"
          >
            {loading ? "Guardando..." : "Guardar candidato"}
          </button>
        </div>

        {success && (
          <p className="md:col-span-2 text-sm text-green-700">{success}</p>
        )}
        {warning && (
          <p className="md:col-span-2 text-sm text-amber-700">{warning}</p>
        )}
        {error && (
          <p className="md:col-span-2 text-sm text-destructive">{error}</p>
        )}
      </form>
    </div>
  );
}
