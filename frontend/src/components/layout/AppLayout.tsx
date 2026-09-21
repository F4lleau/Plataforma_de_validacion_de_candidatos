import LegalAccess from "../legal/LegalAccess";
import { useRef, useState } from "react";
import { NavLink, Outlet, useLocation, Link } from "react-router-dom";
import {
  LayoutDashboard,
  BookUser,
  Settings2,
  Users,
  Files,
  ClipboardCheck,
  ChartNoAxesCombined,
  History,
  CircleHelp,
  UserRoundSearch,
  UserRound,
  LogOut,
  Menu,
  X,
  ChevronRight,
  type LucideIcon,
} from "lucide-react";
import { useAuthStore } from "../../stores/auth.store";
import Brand from "./Brand";

type NavItem = { to: string; label: string; icon: LucideIcon };
const overview: NavItem = {
  to: "/dashboard",
  label: "Resumen",
  icon: LayoutDashboard,
};
const help: NavItem = {
  to: "/ayuda",
  label: "Ayuda y guías",
  icon: CircleHelp,
};
const adminGroups = [
  {
    name: "Espacio de trabajo",
    items: [
      overview,
      { to: "/listas", label: "Listas electorales", icon: Files },
      { to: "/validaciones", label: "Validaciones", icon: ClipboardCheck },
      {
        to: "/candidatos/revision",
        label: "Candidatos en revisión",
        icon: UserRoundSearch,
      },
    ],
  },
  {
    name: "Administración",
    items: [
      { to: "/padron", label: "Padrón de afiliados", icon: BookUser },
      { to: "/usuarios", label: "Apoderados", icon: Users },
      { to: "/configuracion", label: "Configuración", icon: Settings2 },
    ],
  },
  {
    name: "Seguimiento",
    items: [
      { to: "/reportes", label: "Reportes", icon: ChartNoAxesCombined },
      { to: "/auditoria", label: "Auditoría", icon: History },
      { to: "/seguridad", label: "Seguridad de cuenta", icon: UserRound },
      help,
    ],
  },
];
const proxyGroups = [
  {
    name: "Espacio de trabajo",
    items: [
      overview,
      { to: "/listas", label: "Mis listas", icon: Files },
      { to: "/candidatos", label: "Candidatos", icon: UserRound },
      { to: "/seguridad", label: "Seguridad de cuenta", icon: UserRound },
      help,
    ],
  },
];

export default function AppLayout() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuButton = useRef<HTMLButtonElement>(null);
  const location = useLocation();
  const isAdmin = user?.role === "admin";
  const groups = isAdmin ? adminGroups : proxyGroups;
  const current = groups
    .flatMap((g) => g.items)
    .find(
      (i) =>
        location.pathname === i.to || location.pathname.startsWith(i.to + "/"),
    );
  const role = isAdmin ? "Administración" : "Apoderado";
  return (
    <div className="min-h-screen">
      <a className="skip-link" href="#contenido">
        Saltar al contenido
      </a>
      <div className="flex items-center justify-between border-b bg-card px-5 py-4 lg:hidden">
        <Brand />
        <button
          ref={menuButton}
          type="button"
          className="secondary !p-2.5"
          aria-label={menuOpen ? "Cerrar menú" : "Abrir menú"}
          aria-expanded={menuOpen}
          aria-controls="navigation-panel"
          onKeyDown={(event) => {
            if (event.key === "Escape") setMenuOpen(false);
          }}
          onClick={() => setMenuOpen(!menuOpen)}
        >
          {menuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>
      <div className="lg:flex">
        <aside
          id="navigation-panel"
          className={`${menuOpen ? "flex" : "hidden"} shrink-0 flex-col border-b bg-card lg:sticky lg:top-0 lg:flex lg:h-screen lg:w-64 lg:overflow-y-auto lg:border-b-0 lg:border-r`}
          onKeyDown={(e) => {
            if (e.key === "Escape") {
              setMenuOpen(false);
              menuButton.current?.focus();
            }
          }}
        >
          <div className="hidden px-6 py-7 lg:block">
            <Brand />
          </div>
          <nav
            aria-label="Navegación principal"
            className="flex-1 space-y-6 px-4 py-5 lg:pt-3"
          >
            {groups.map((group) => (
              <div key={group.name}>
                <p className="eyebrow mb-2 px-3">{group.name}</p>
                <div className="space-y-1">
                  {group.items.map(({ to, label, icon: Icon }) => (
                    <NavLink
                      key={to}
                      to={to}
                      onClick={() => {
                        setMenuOpen(false);
                        if (menuOpen) menuButton.current?.focus();
                      }}
                      className={({ isActive }) =>
                        `flex min-h-11 items-center gap-3 rounded-lg px-3 py-2.5 text-[13px] font-medium transition-colors ${isActive ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:bg-muted hover:text-foreground"}`
                      }
                    >
                      <Icon size={18} strokeWidth={1.7} aria-hidden="true" />
                      <span>{label}</span>
                    </NavLink>
                  ))}
                </div>
              </div>
            ))}
          </nav>
          <div className="mx-5 mb-5 border-t pt-4">
            <p className="eyebrow">Plataforma PJ</p>
            <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
              Gestión de listas y validación
              <br />
              de candidatos.
            </p>
          </div>
        </aside>
        <div className="min-w-0 flex-1">
          <header className="flex min-h-[76px] flex-wrap items-center justify-between gap-3 border-b bg-card/90 px-5 py-4 md:px-8">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span className="hidden sm:inline">Gestión electoral</span>
              <ChevronRight
                className="hidden sm:block"
                size={14}
                aria-hidden="true"
              />
              <span className="font-medium text-foreground">
                {current?.label ?? "Plataforma"}
              </span>
            </div>
            <div className="flex min-w-0 items-center gap-3">
              <span
                className="flex size-9 shrink-0 items-center justify-center rounded-full border bg-muted text-xs font-semibold text-muted-foreground"
                aria-hidden="true"
              >
                {user?.full_name
                  ?.split(" ")
                  .filter(Boolean)
                  .slice(0, 2)
                  .map((n) => n[0])
                  .join("")}
              </span>
              <div className="max-w-40">
                <p className="truncate text-xs font-semibold">
                  {user?.full_name}
                </p>
                <p className="mt-0.5 text-[11px] text-muted-foreground">
                  {role}
                </p>
              </div>
              <button
                type="button"
                onClick={() => {
                  void logout().catch(() =>
                    alert(
                      "Se cerró la sesión en este navegador, pero no se pudo confirmar el cierre en el servidor. Intentá nuevamente cuando vuelva la conexión.",
                    ),
                  );
                }}
                className="secondary !min-h-10 !p-2.5"
                aria-label="Cerrar sesión"
                title="Cerrar sesión"
              >
                <LogOut size={17} aria-hidden="true" />
              </button>
            </div>
          </header>
          <main
            id="contenido"
            tabIndex={-1}
            className="app-content mx-auto max-w-[1500px] p-5 outline-none md:p-8 xl:px-10 xl:py-9"
          >
            <Outlet />
          </main>
          <footer className="mx-5 flex flex-wrap justify-between gap-2 border-t py-5 text-[11px] text-muted-foreground md:mx-8 xl:mx-10">
            <span>Junta Electoral · Partido Justicialista · Chaco</span>
            <Link to="/ayuda" className="hover:text-primary">
              Ayuda y documentación
            </Link>
            <div className="w-full pt-2">
              <LegalAccess />
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}
