import type { TableData } from "../types/analysis";

interface TableViewerProps {
  tables: TableData[];
}

export const TableViewer = ({ tables }: TableViewerProps) => {
  console.log("📋 TableViewer rendering with", tables.length, "tables");

  if (tables.length === 0) {
    console.log("⚠️ No tables to display");
    return null;
  }

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-bold mb-4 text-primary-dark">Tableaux de résultats</h2>
      <div className="space-y-6">
        {tables.map((table, idx) => (
          <div key={idx} className="bg-white p-4 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-3 text-gray-700">{table.name}</h3>
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
                  {table.rows.map((row, rowIdx) => (
                    <tr key={rowIdx}>
                      {table.columns.map((col, colIdx) => (
                        <td key={colIdx}>{row[col]}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
