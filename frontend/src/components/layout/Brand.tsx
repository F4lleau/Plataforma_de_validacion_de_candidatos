import { Layers3 } from "lucide-react";
export default function Brand() {
  return (
    <div className="flex items-center gap-3">
      <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary text-white">
        <Layers3 size={21} aria-hidden="true" />
      </span>
      <div>
        <p className="text-sm font-bold tracking-tight">Junta Electoral</p>
        <p className="mt-0.5 text-xs text-muted-foreground">
          PJ · Distrito Chaco
        </p>
      </div>
    </div>
  );
}
