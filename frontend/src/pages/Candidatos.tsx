import { Link } from "react-router-dom";
export default function Candidatos() {
  return (
    <section className="space-y-4">
      <h1 className="font-heading text-3xl font-bold">Candidatos</h1>
      <p>
        Seleccioná la lista para cargar candidatos en sus posiciones, guardar
        borradores y consultar las validaciones.
      </p>
      <Link className="action inline-block" to="/listas">
        Ir a mis listas
      </Link>
    </section>
  );
}
