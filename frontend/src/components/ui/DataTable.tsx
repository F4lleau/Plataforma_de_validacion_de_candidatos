import type { ReactNode } from "react";
import { FileSpreadsheet } from "lucide-react";
import { formatDate } from "../../utils/date";

type DataCell = ReactNode;

export type DataColumn<T extends Record<string, DataCell>> = {
  key: keyof T & string;
  label: string;
  className?: string;
};

export function DataTable<T extends Record<string, DataCell>>({
  columns,
  rows,
  rowKey,
  emptyText = "No hay resultados",
}: {
  columns: DataColumn<T>[];
  rows: T[];
  rowKey: (row: T) => string | number;
  emptyText?: string;
}) {
  return (
    <div className="overflow-hidden rounded-lg border border-[#cfe1e7] bg-white">
      <div className="max-w-full overflow-x-auto">
        <table className="min-w-[1240px] table-fixed text-left font-mono text-[11px]">
          <thead className="bg-[#00384a] text-white">
            <tr>
              {columns.map((column) => (
                <th
                  className={`border-r border-white/10 px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.08em] last:border-r-0 ${column.className ?? ""}`}
                  key={column.key}
                >
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr
                className="odd:bg-white even:bg-[#f5fbfd] hover:bg-[#eaf6fa]"
                key={rowKey(row)}
              >
                {columns.map((column) => (
                  <td
                    className="border-b border-[#d8e8ee] px-3 py-1.5 align-middle text-[#14384a]"
                    key={column.key}
                  >
                    {formatCell(row[column.key], column.key)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {rows.length === 0 && (
        <div className="grid min-h-28 place-items-center border-t border-[#d8e8ee] bg-[#f5fbfd] px-4 py-6 text-center">
          <div>
            <FileSpreadsheet
              className="mx-auto mb-2 text-[#5f8fa1]"
              size={22}
              aria-hidden="true"
            />
            <p className="font-mono text-[11px] font-semibold uppercase tracking-[0.12em] text-[#00384a]">
              {emptyText}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function formatCell(value: DataCell, key: string) {
  if (value === null || value === undefined || value === "") return "";
  if (
    typeof value === "string" &&
    (key.endsWith("_date") || key.includes("date"))
  )
    return formatDate(value);
  return value;
}
