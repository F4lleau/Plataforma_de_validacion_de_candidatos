export default function Forbidden() {
  return (
    <div className="mx-auto max-w-xl py-16 text-center">
      <h1 className="font-heading text-3xl font-bold">Acceso restringido</h1>
      <p className="mt-3 text-muted-foreground">
        Tu rol no tiene permisos para acceder a esta sección.
      </p>
    </div>
  );
}
