import { NavLink, Outlet } from "react-router-dom";
import { useAuthStore } from "../../stores/auth.store";

export default function AppLayout() {
  const { user, logout } = useAuthStore();
  const isAdmin = user?.role === "admin";

  const links = isAdmin
    ? [
        ["/dashboard", "Dashboard"],
        ["/padron", "Padrón"],
        ["/listas", "Listas"],
        ["/candidatos/revision", "Candidatos en revisión"],
      ]
    : [
        ["/dashboard", "Dashboard"],
        ["/listas", "Mis listas"],
        ["/candidatos", "Candidatos"],
      ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="flex min-h-screen">
        <aside className="hidden w-64 shrink-0 border-r bg-card p-5 md:block">
          <div className="mb-10">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-primary">
              Junta Electoral
            </p>
            <h1 className="mt-2 font-heading text-xl font-bold">
              Plataforma PJ
            </h1>
          </div>
          <nav className="space-y-1">
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
          <header className="flex items-center justify-between border-b bg-card px-5 py-4">
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
