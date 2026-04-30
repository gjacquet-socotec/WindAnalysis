import { useState } from "react";
import type { WorkflowType } from "../types/analysis";

interface ConfigPanelProps {
  onSubmit: (folderPath: string, workflowType: WorkflowType) => void;
  isLoading: boolean;
}

export const ConfigPanel = ({ onSubmit, isLoading }: ConfigPanelProps) => {
  const [folderPath, setFolderPath] = useState("");
  const [workflowType, setWorkflowType] = useState<WorkflowType>("runtest");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (folderPath.trim()) {
      onSubmit(folderPath, workflowType);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4 text-primary-dark">Configuration</h2>

      <div className="mb-4">
        <label className="block text-gray-700 font-semibold mb-2">
          Chemin du dossier de données
        </label>
        <input
          type="text"
          value={folderPath}
          onChange={(e) => setFolderPath(e.target.value)}
          placeholder="C:\Users\...\experiments\real_run_test"
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-dark"
          disabled={isLoading}
        />
      </div>

      <div className="mb-4">
        <label className="block text-gray-700 font-semibold mb-2">
          Type d'analyse
        </label>
        <select
          value={workflowType}
          onChange={(e) => setWorkflowType(e.target.value as WorkflowType)}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-dark"
          disabled={isLoading}
        >
          <option value="runtest">RunTest (Réception)</option>
          <option value="scada">SCADA (Surveillance)</option>
        </select>
      </div>

      <button
        type="submit"
        disabled={isLoading || !folderPath.trim()}
        className="w-full bg-primary-dark text-white py-3 rounded-md font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
      >
        {isLoading ? (
          <>
            <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Analyse en cours...
          </>
        ) : (
          "Valider"
        )}
      </button>
    </form>
  );
};
