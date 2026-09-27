import { Layers3 } from "lucide-react";

export default function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <div className={`flex items-center ${compact ? "justify-center" : "gap-3"}`}>
      <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-[#0b84a5] text-white shadow-sm">
        <Layers3 size={21} aria-hidden="true" />
      </span>
      <div className={compact ? "sr-only" : ""}>
        <p className="text-sm font-bold tracking-tight text-[#00384a]">
          Junta Electoral
        </p>
        <p className="mt-0.5 text-xs text-[#5f8fa1]">PJ · Distrito Chaco</p>
      </div>
    </div>
  );
}
