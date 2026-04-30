import { usePagination } from '../../hooks/usePagination';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import type { TableData } from '../../types/analysis';

interface PaginatedTableProps {
  table: TableData;
  itemsPerPage?: number;
}

export function PaginatedTable({ table, itemsPerPage = 10 }: PaginatedTableProps) {
  const pagination = usePagination({
    totalItems: table.rows.length,
    itemsPerPage,
  });

  const currentRows = pagination.getCurrentPageItems(table.rows);
  const needsPagination = table.rows.length > itemsPerPage;

  return (
    <div className="space-y-4">
      {/* Table */}
      <div className="overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              {table.columns.map((col, colIdx) => (
                <th key={colIdx}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentRows.map((row, rowIdx) => (
              <tr key={rowIdx}>
                {table.columns.map((col, colIdx) => (
                  <td key={colIdx}>{row[col]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      {needsPagination && (
        <div className="flex items-center justify-between border-t border-gray-200 pt-4">
          {/* Info */}
          <div className="text-sm text-gray-600">
            Affichage de {pagination.startIndex + 1} à {pagination.endIndex} sur {table.rows.length} lignes
          </div>

          {/* Navigation */}
          <div className="flex items-center space-x-2">
            <button
              onClick={pagination.goToFirst}
              disabled={!pagination.canGoPrevious}
              className="p-2 rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Première page"
            >
              <ChevronsLeft className="w-5 h-5" />
            </button>

            <button
              onClick={pagination.goPrevious}
              disabled={!pagination.canGoPrevious}
              className="p-2 rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Page précédente"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            <span className="px-4 py-2 text-sm font-medium text-gray-700">
              Page {pagination.currentPage} / {pagination.totalPages}
            </span>

            <button
              onClick={pagination.goNext}
              disabled={!pagination.canGoNext}
              className="p-2 rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Page suivante"
            >
              <ChevronRight className="w-5 h-5" />
            </button>

            <button
              onClick={pagination.goToLast}
              disabled={!pagination.canGoNext}
              className="p-2 rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Dernière page"
            >
              <ChevronsRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
