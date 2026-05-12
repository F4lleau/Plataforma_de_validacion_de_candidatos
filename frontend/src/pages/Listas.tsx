import { useEffect, useState } from "react";
import { getListTemplate } from "../services/lists.service";

export default function Listas() {
  const [template, setTemplate] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadTemplate = async () => {
      try {
        const data = await getListTemplate("consejo_local");
        setTemplate(data as any[]);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    loadTemplate();
  }, []);

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="font-heading text-3xl font-bold text-foreground">
          Plantilla de lista
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Estructura base de la lista para Consejo Local.
        </p>
      </div>

      <div className="rounded-lg border bg-card p-6 shadow-sm">
        {loading ? (
          <p className="text-sm text-muted-foreground">Cargando plantilla...</p>
        ) : (
          <div className="space-y-3">
            {template.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between rounded-md border p-3"
              >
                <div>
                  <p className="font-medium text-foreground">{item.name}</p>
                  <p className="text-sm text-muted-foreground">
                    Grupo: {item.group_name}
                  </p>
                </div>
                <span className="rounded-full bg-accent px-3 py-1 text-xs font-medium text-accent-foreground">
                  Posición {item.position_order}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}