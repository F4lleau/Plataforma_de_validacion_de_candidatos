import { useState } from "react";

export default function Candidatos() {
  const [form, setForm] = useState({
    dni: "",
    first_name: "",
    last_name: "",
    birth_date: "",
    gender: "",
    cargo_label: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Candidato a enviar:", form);
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

        <div className="md:col-span-2">
          <button
            type="submit"
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90"
          >
            Guardar candidato
          </button>
        </div>
      </form>
    </div>
  );
}