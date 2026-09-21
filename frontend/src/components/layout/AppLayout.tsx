import { NavLink, Outlet } from "react-router-dom";
import { useAuthStore } from "../../stores/auth.store";

export default function AppLayout() {
  const { user, logout } = useAuthStore();
  const isAdmin = user?.role === "admin";

  const links = isAdmin
    ? [
        ["/dashboard", "Dashboard"],
        ["/padron", "Padrón"],
        ["/configuracion", "Configuración"],
        ["/usuarios", "Apoderados"],
        ["/listas", "Listas"],
        ["/validaciones", "Listas cargadas / Validaciones"],
        ["/reportes", "Reportes"],
        ["/auditoria", "Auditoría"],
        ["/ayuda", "Ayuda"],
        ["/candidatos/revision", "Candidatos en revisión"],
      ]
    : [
        ["/dashboard", "Dashboard"],
        ["/listas", "Mis listas"],
        ["/candidatos", "Candidatos"],
        ["/ayuda", "Ayuda"],
      ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="flex min-h-screen flex-col md:flex-row">
        <aside className="w-full shrink-0 border-b bg-card p-5 md:w-64 md:border-b-0 md:border-r">
          <div className="mb-4 md:mb-10">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-primary">
              Junta Electoral
            </p>
            <p className="mt-2 font-heading text-xl font-bold">Plataforma PJ</p>
          </div>
          <nav
            aria-label="Navegación principal"
            className="flex flex-wrap gap-1 md:block md:space-y-1"
          >
            {links.map(([to, label]) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `block rounded-md px-3 py-2 text-sm ${isActive ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-muted"}`
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>
        </aside>

        <div className="min-w-0 flex-1">
          <header className="flex flex-wrap items-center justify-between gap-4 border-b bg-card px-5 py-4">
            <div>
              <p className="font-heading font-semibold">Gestión electoral</p>
              <p className="text-xs text-muted-foreground">
                Validación de candidatos
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium">{user?.full_name}</p>
                <p className="text-xs uppercase text-muted-foreground">
                  {user?.role}
                </p>
              </div>
              <button
                type="button"
                onClick={logout}
                className="rounded-md border px-3 py-2 text-sm hover:bg-muted"
              >
                Cerrar sesión
              </button>
            </div>
          </header>
          <main className="mx-auto max-w-7xl p-4 md:p-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
