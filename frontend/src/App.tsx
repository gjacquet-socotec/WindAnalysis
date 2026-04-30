import { useState } from "react";
import { ConfigPanel } from "./components/ConfigPanel";
import { ChartViewer } from "./components/ChartViewer";
import { TableViewer } from "./components/TableViewer";
import { ErrorNotification } from "./components/ErrorNotification";
import { DebugViewer } from "./components/DebugViewer";
import { analyzeAPI } from "./services/api";
import type { AnalyzeResponse, WorkflowType } from "./types/analysis";

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (folderPath: string, workflowType: WorkflowType) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      console.log("📤 Sending request:", { folder_path: folderPath, workflow_type: workflowType });
      const response = await analyzeAPI.runAnalysis({
        folder_path: folderPath,
        workflow_type: workflowType,
        render_template: true,
      });
      console.log("📥 Response received:", response);
      console.log("  - Status:", response.status);
      console.log("  - Charts:", response.charts?.length);
      console.log("  - Tables:", response.tables?.length);
      setResult(response);
    } catch (err: any) {
      console.error("❌ Error:", err);
      const errorMessage = err.response?.data?.detail || err.message || "Erreur inconnue";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-primary-dark text-white py-6 shadow-md">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold">Wind Turbine Analytics Dashboard</h1>
          <p className="text-sm mt-1">Plateforme d'analyse de performance d'éoliennes</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Sidebar Configuration */}
          <div className="lg:col-span-1">
            <ConfigPanel onSubmit={handleAnalyze} isLoading={isLoading} />

            {result?.metadata && (
              <div className="mt-4 bg-white p-4 rounded-lg shadow-md">
                <h3 className="font-bold text-primary-dark mb-2">Informations</h3>
                <p className="text-sm"><strong>Parc :</strong> {result.metadata.park_name}</p>
                <p className="text-sm"><strong>Turbines :</strong> {result.metadata.turbines?.join(", ")}</p>
                <p className="text-sm"><strong>Période :</strong> {result.metadata.test_start} → {result.metadata.test_end}</p>
                {result.report_path && (
                  <p className="text-sm mt-2"><strong>Rapport :</strong> <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">{result.report_path}</code></p>
                )}
              </div>
            )}
          </div>

          {/* Results Area */}
          <div className="lg:col-span-2">
            {result ? (
              <>
                <DebugViewer result={result} />
                <ChartViewer charts={result.charts} />
                <TableViewer tables={result.tables} />
              </>
            ) : (
              <div className="text-center text-gray-500 mt-20">
                <p>Aucune analyse en cours. Utilisez le panneau de configuration pour démarrer.</p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Error Notification */}
      {error && <ErrorNotification message={error} onClose={() => setError(null)} />}
    </div>
  );
}

export default App;
