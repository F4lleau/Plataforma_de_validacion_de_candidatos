import { PageHeading } from "../components/forms/FormUI";
import { Link } from "react-router-dom";
export default function Candidatos() {
  return (
    <section className="space-y-4">
      <PageHeading eyebrow="Carga de candidatos" title="Candidatos" />
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
