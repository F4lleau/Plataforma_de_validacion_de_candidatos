import { PageHeading } from "../components/forms/FormUI";
import { useAuthStore } from "../stores/auth.store";
import { useRemote } from "../hooks/useRemote";
import { Panel, Feedback } from "../components/forms/FormUI";
export default function Ayuda() {
  const admin = useAuthStore((s) => s.user?.role === "admin");
  const support = useRemote<{ contact: string }>("/auth/support");
  return (
    <div className="space-y-6">
      <PageHeading
        eyebrow="Documentación"
        title="Ayuda y soporte"
        description="Guías para acompañarte en cada etapa de la gestión electoral."
      />
      <Panel
        title={admin ? "Guía para administración" : "Guía para apoderados"}
      >
        <ol className="list-decimal space-y-3 pl-5">
          {(admin
            ? [
                "Configurá elección, fechas, cargos y reglas. Las plantillas de prueba deben seguir identificadas.",
                "Creá apoderados y habilitá sus módulos. La asignación por lista es independiente.",
                "Importá el padrón XLSX. Si hay errores, el lote previo permanece vigente.",
                "Revisá Listas cargadas y Validaciones, incluyendo cada observación del candidato.",
                "Consultá Reportes para filtrar y exportar. Auditoría registra el actor y la fecha.",
              ]
            : [
                "Creá o abrí una lista asignada desde Mis listas.",
                "Cargá cada candidato en su posición. Guardar borrador conserva la identidad mínima.",
                "Usá Guardar y validar para consultar afiliación, requisitos y RENAPER. Una ausencia en padrón no impide guardar.",
                "Corregí la composición hasta completar todas las posiciones y las reglas configuradas.",
                "Enviá la lista para revisión. Después del envío queda en lectura; enviada no significa aprobada.",
              ]
          ).map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </Panel>
      <Panel title="Problemas frecuentes">
        <div className="divide-y">
          {[
            [
              "¿Qué hago si vence la sesión o aparece un error de red?",
              "Si la sesión vence, ingresá nuevamente. Ante un error de red, recargá el detalle antes de repetir: el guardado podría haberse completado.",
            ],
            [
              "¿Por qué no veo una lista?",
              "El administrador debe comprobar tanto la asignación de la lista como el módulo habilitado. No se conceden permisos por compartir localidad.",
            ],
            [
              "¿Qué sucede si falla la importación del padrón?",
              "Una importación fallida no cambia el padrón vigente. Revisá las filas indicadas en el historial y volvé a subir el archivo completo.",
            ],
            [
              "¿Cuál es el estado de RENAPER?",
              "RENAPER está pendiente de conexión real. Los datos de prueba no acreditan cumplimiento institucional.",
            ],
          ].map(([question, answer]) => (
            <details key={question} className="py-3">
              <summary className="cursor-pointer text-sm font-medium">
                {question}
              </summary>
              <p className="pb-2 pt-3 text-sm leading-relaxed text-muted-foreground">
                {answer}
              </p>
            </details>
          ))}
        </div>
      </Panel>
      <Panel title="Contacto y recuperación">
        <Feedback error={support.error} />
        <p>
          {support.data?.contact ||
            "Contactá al administrador de la Junta por tu canal habitual. El contacto institucional todavía no fue configurado."}
        </p>
        <p>
          Usá «Olvidé mi contraseña» en el ingreso para recibir un enlace por
          correo. El administrador también puede enviarte la recuperación o
          retirar un bloqueo temporal. Para informar un error, indicá pantalla,
          operación, fecha y número de lista; no compartas tu contraseña.
        </p>
      </Panel>
    </div>
  );
}
