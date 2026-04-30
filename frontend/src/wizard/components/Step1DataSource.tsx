import { useState } from 'react';
import { useWizard } from '../../hooks/useWizard';
import type { WorkflowType } from '../../types/analysis';

export function Step1DataSource() {
  const { state, setFolderPath, setWorkflowType, nextStep, setError } = useWizard();

  const [localFolderPath, setLocalFolderPath] = useState(state.folderPath || '');
  const [localWorkflowType, setLocalWorkflowType] = useState<WorkflowType>(
    state.workflowType || 'runtest'
  );

  const handleValidate = () => {
    // Validation
    if (!localFolderPath.trim()) {
      setError('Veuillez entrer un chemin de dossier valide');
      return;
    }

    // Save to context
    setFolderPath(localFolderPath);
    setWorkflowType(localWorkflowType);
    setError(null);

    // Auto-advance to next step
    nextStep();
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-primary-dark mb-6">
        Étape 1 : Sélection de la source de données
      </h2>

      <div className="space-y-6">
        {/* Folder Path Input */}
        <div>
          <label htmlFor="folderPath" className="block text-gray-700 font-semibold mb-2">
            Chemin du dossier contenant config.yml
          </label>
          <input
            type="text"
            id="folderPath"
            value={localFolderPath}
            onChange={(e) => setLocalFolderPath(e.target.value)}
            placeholder="C:\Users\...\experiments\real_run_test"
            className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-dark text-lg"
          />
          <p className="mt-2 text-sm text-gray-600">
            Le dossier doit contenir un fichier <code className="bg-gray-100 px-1 py-0.5 rounded">config.yml</code> valide.
          </p>
        </div>

        {/* Workflow Type Selection */}
        <div>
          <label htmlFor="workflowType" className="block text-gray-700 font-semibold mb-2">
            Type d'analyse
          </label>
          <select
            id="workflowType"
            value={localWorkflowType}
            onChange={(e) => setLocalWorkflowType(e.target.value as WorkflowType)}
            className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-dark text-lg"
          >
            <option value="runtest">RunTest - Réception d'éolienne</option>
            <option value="scada">SCADA - Surveillance continue</option>
          </select>
          <p className="mt-2 text-sm text-gray-600">
            {localWorkflowType === 'runtest'
              ? 'Analyse pour réception : 120h consécutives, puissance nominale, disponibilité.'
              : 'Analyse SCADA : EBA, codes d\'erreur, calibration, disponibilité des données.'}
          </p>
        </div>

        {/* Information Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <h3 className="font-semibold text-blue-900 mb-2">ℹ️ Information</h3>
          <p className="text-sm text-blue-800">
            À l'étape suivante, vous pourrez revoir la configuration avant de lancer l'analyse.
            Le traitement peut prendre entre 1 et 5 minutes selon la quantité de données.
          </p>
        </div>

        {/* Action Button */}
        <div className="flex justify-end pt-4">
          <button
            onClick={handleValidate}
            disabled={!localFolderPath.trim()}
            className="bg-primary-dark text-white px-8 py-3 rounded-md font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            Continuer vers la configuration →
          </button>
        </div>
      </div>
    </div>
  );
}
