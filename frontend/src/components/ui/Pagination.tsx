import { ChevronLeft, ChevronRight } from "lucide-react";
import { ActionButton } from "./ActionUI";

const numberFormat = new Intl.NumberFormat("es-AR");

export function Pagination({
  page,
  pageSize,
  total,
  onPageChange,
}: {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
}) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const firstRow = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const lastRow = Math.min(page * pageSize, total);

  return (
    <nav
      aria-label="Paginación"
      className="flex flex-wrap items-center justify-center gap-3 border-t border-[#d8e8ee] pt-4"
    >
      <ActionButton
        type="button"
        variant="secondary"
        className="!min-h-9 !px-3"
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
        aria-label="Página anterior"
      >
        <ChevronLeft size={15} aria-hidden="true" />
        Anterior
      </ActionButton>
      <div className="inline-flex min-h-9 items-center rounded-full bg-[#00384a] px-4 font-mono text-[11px] font-semibold uppercase tracking-[0.09em] text-white shadow-sm">
        Página {page} de {totalPages}
        <span className="ml-2 text-white/70">
          {numberFormat.format(firstRow)}-{numberFormat.format(lastRow)} de{" "}
          {numberFormat.format(total)}
        </span>
      </div>
      <ActionButton
        type="button"
        variant="secondary"
        className="!min-h-9 !px-3"
        disabled={page >= totalPages}
        onClick={() => onPageChange(page + 1)}
        aria-label="Página siguiente"
      >
        Siguiente
        <ChevronRight size={15} aria-hidden="true" />
      </ActionButton>
    </nav>
  );
}
