import type { AnalyzeResponse } from "../types/analysis";

interface DebugViewerProps {
  result: AnalyzeResponse | null;
}

export const DebugViewer = ({ result }: DebugViewerProps) => {
  if (!result) return null;

  return (
    <div className="mt-8 bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
      <h3 className="text-lg font-bold mb-2 text-yellow-800">🔍 Debug Info</h3>
      <div className="space-y-2 text-sm">
        <p><strong>Status:</strong> {result.status}</p>
        <p><strong>Message:</strong> {result.message}</p>
        <p><strong>Charts count:</strong> {result.charts?.length || 0}</p>
        <p><strong>Tables count:</strong> {result.tables?.length || 0}</p>

        {result.charts && result.charts.length > 0 && (
          <div>
            <p className="font-bold mt-2">Charts:</p>
            <ul className="list-disc ml-6">
              {result.charts.map((chart, idx) => (
                <li key={idx}>
                  {chart.name}
                  {chart.plotly_json?.data ? ` (${chart.plotly_json.data.length} traces)` : ' (no data)'}
                </li>
              ))}
            </ul>
          </div>
        )}

        {result.tables && result.tables.length > 0 && (
          <div>
            <p className="font-bold mt-2">Tables:</p>
            <ul className="list-disc ml-6">
              {result.tables.map((table, idx) => (
                <li key={idx}>
                  {table.name} ({table.rows?.length || 0} rows, {table.columns?.length || 0} cols)
                </li>
              ))}
            </ul>
          </div>
        )}

        <details className="mt-4">
          <summary className="cursor-pointer font-bold text-yellow-800 hover:text-yellow-900">
            View raw JSON (click to expand)
          </summary>
          <pre className="mt-2 p-2 bg-white rounded border overflow-auto max-h-96 text-xs">
            {JSON.stringify(result, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  );
};
