import { useAuthStore } from "../stores/auth.store";

export default function Dashboard() {
  const user = useAuthStore((state) => state.user);
  return (
    <div>
      <h1 className="font-heading text-3xl font-bold">
        Bienvenido, {user?.full_name}
      </h1>
      <p className="mt-2 text-muted-foreground">
        Gestioná la validación electoral desde tu espacio de trabajo.
      </p>
    </div>
  );
}
