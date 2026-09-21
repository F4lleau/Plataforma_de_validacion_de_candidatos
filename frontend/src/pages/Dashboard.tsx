import { useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowUpRight,
  ClipboardCheck,
  Files,
  BookUser,
  ChartNoAxesCombined,
  CircleHelp,
} from "lucide-react";
import { useAuthStore } from "../stores/auth.store";
import { useRemote } from "../hooks/useRemote";
import {
  Field,
  Feedback,
  Panel,
  PageHeading,
} from "../components/forms/FormUI";
import { Metrics, ListTable } from "../components/reporting/ReportUI";
import StatusBadge from "../components/reporting/StatusBadge";
import type { Election } from "../services/management.service";
import { stateLabels, type Summary } from "../services/reporting.service";

export default function Dashboard() {
  const user = useAuthStore((s) => s.user);
  const admin = user?.role === "admin";
  const [election, setElection] = useState("");
  const elections = useRemote<Election[]>("/elections/");
  const data = useRemote<Summary>(
    `/dashboard/summary${election ? `?election_id=${election}` : ""}`,
  );
  const shortcuts = admin
    ? [
        {
          to: "/validaciones",
          title: "Revisar listas",
          description: "Composición y controles",
          icon: ClipboardCheck,
        },
        {
          to: "/padron",
          title: "Consultar padrón",
          description: "Afiliación partidaria",
          icon: BookUser,
        },
        {
          to: "/reportes",
          title: "Ver reportes",
          description: "Indicadores y exportaciones",
          icon: ChartNoAxesCombined,
        },
      ]
    : [
        {
          to: "/listas",
          title: "Mis listas",
          description: "Crear o continuar la carga",
          icon: Files,
        },
        {
          to: "/candidatos",
          title: "Candidatos",
          description: "Consultar candidatos",
          icon: ClipboardCheck,
        },
        {
          to: "/ayuda",
          title: "Guía del apoderado",
          description: "Cómo completar y enviar",
          icon: CircleHelp,
        },
      ];
  return (
    <div className="space-y-7">
      <PageHeading
        eyebrow={admin ? "Panel de administración" : "Espacio del apoderado"}
        title={`Bienvenido, ${user?.full_name ?? ""}`}
        description="Toda la gestión electoral, en un solo lugar. Consultá el avance de las listas y continuá con tu trabajo."
      >
        <Link className="action" to={admin ? "/validaciones" : "/listas"}>
          {admin ? "Revisar listas" : "Ir a mis listas"}
          <ArrowUpRight size={16} aria-hidden="true" />
        </Link>
      </PageHeading>
      <div className="flex flex-wrap items-center justify-between gap-4 border-y py-4">
        <div>
          <p className="text-sm font-semibold">Resumen electoral</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Información del alcance que selecciones.
          </p>
        </div>
        <div className="w-full sm:w-80">
          <Field label="Alcance electoral">
            <select
              className="field"
              value={election}
              onChange={(e) => setElection(e.target.value)}
            >
              <option value="">Todas las elecciones autorizadas</option>
              {elections.data?.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.name}
                </option>
              ))}
            </select>
          </Field>
        </div>
      </div>
      <Feedback error={data.error || elections.error} />
      {data.loading && (
        <p
          role="status"
          className="rounded-xl border bg-card p-6 text-sm text-muted-foreground"
        >
          Cargando resumen electoral...
        </p>
      )}
      {data.data && (
        <>
          <Metrics data={data.data} />
          <p className="!mt-3 text-xs text-muted-foreground">
            Aprobación sobre {data.data.approval_denominator} listas del alcance
            seleccionado. Cada lista se cuenta en un único estado.
          </p>
          <div className="grid gap-5 xl:grid-cols-[1.4fr_1fr]">
            <Panel title="Estado de las listas">
              <div className="space-y-4">
                {Object.entries(stateLabels).map(([key]) => (
                  <div
                    key={key}
                    className="grid grid-cols-[minmax(0,1fr)_72px_28px] items-center gap-3 sm:grid-cols-[minmax(0,1fr)_120px_36px]"
                  >
                    <div>
                      <StatusBadge status={key} />
                    </div>
                    <div
                      className="h-1.5 overflow-hidden rounded-full bg-muted"
                      aria-hidden="true"
                    >
                      <div
                        className="h-full rounded-full bg-primary/75"
                        style={{
                          width: `${(100 * (data.data?.by_status[key] ?? 0)) / Math.max(data.data?.total_lists ?? 0, 1)}%`,
                        }}
                      />
                    </div>
                    <span className="text-right font-mono text-xs">
                      {data.data?.by_status[key] ?? 0}
                    </span>
                  </div>
                ))}
              </div>
              <p className="border-t pt-4 text-xs leading-relaxed text-muted-foreground">
                {admin
                  ? `${data.data.sent_lists} listas enviadas para revisión administrativa.`
                  : "Las listas enviadas quedan disponibles en modo lectura."}{" "}
                El envío no equivale a aprobación.
              </p>
            </Panel>
            <Panel title="Accesos rápidos">
              <div className="space-y-2">
                {shortcuts.map(({ to, title, description, icon: Icon }) => (
                  <Link
                    key={to}
                    to={to}
                    className="group flex items-center gap-3 rounded-xl border border-transparent p-3 transition-colors hover:border-primary/15 hover:bg-accent/50"
                  >
                    <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-accent text-primary">
                      <Icon size={19} strokeWidth={1.6} aria-hidden="true" />
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold">{title}</p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {description}
                      </p>
                    </div>
                    <ArrowUpRight
                      size={16}
                      className="text-muted-foreground group-hover:text-primary"
                      aria-hidden="true"
                    />
                  </Link>
                ))}
              </div>
            </Panel>
          </div>
          {!admin && (
            <Panel title="Mis módulos">
              <div className="grid gap-3 sm:grid-cols-2">
                {data.data.modules?.length === 0 ? (
                  <p className="text-sm text-muted-foreground">
                    No tenés módulos habilitados. Solicitá la asignación al
                    administrador.
                  </p>
                ) : (
                  data.data.modules?.map((m) => (
                    <article
                      className="rounded-xl border bg-muted/30 p-4"
                      key={m.id}
                    >
                      <p className="text-sm font-semibold">
                        {m.office_name} · {m.municipality_name}
                      </p>
                      <p className="mt-2 text-xs text-muted-foreground">
                        {m.election_name}
                      </p>
                    </article>
                  ))
                )}
              </div>
              <Link className="text-link" to="/listas">
                Crear lista / continuar carga{" "}
                <ArrowUpRight size={15} aria-hidden="true" />
              </Link>
            </Panel>
          )}
          <Panel title="Últimas listas">
            <ListTable items={data.data.recent_lists ?? []} />
            <Link
              className="text-link"
              to={admin ? "/validaciones" : "/listas"}
            >
              Ver todas las listas <ArrowUpRight size={15} aria-hidden="true" />
            </Link>
          </Panel>
        </>
      )}
    </div>
  );
}
