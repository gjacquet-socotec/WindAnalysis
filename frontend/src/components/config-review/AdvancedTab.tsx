import type { ParsedConfig } from '../../types/config';
import { Settings, FileText, AlertCircle, CheckCircle } from 'lucide-react';

interface AdvancedTabProps {
  config: ParsedConfig;
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return <h4 className="text-md font-bold text-gray-700 mb-3 mt-6 first:mt-0">{children}</h4>;
}

export function AdvancedTab({ config }: AdvancedTabProps) {
  const { render_template, template_path, output_path, log_data } = config;

  return (
    <div className="space-y-6">
      {/* Paramètres de génération de rapport */}
      <div>
        <SectionTitle>Paramètres de génération de rapport</SectionTitle>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
            <div className="flex-shrink-0 mt-1 text-primary-dark">
              <Settings className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-500">Génération du rapport</p>
              <p className="text-lg font-semibold text-gray-900">
                {render_template ? (
                  <span className="flex items-center space-x-2 text-green-600">
                    <CheckCircle className="w-5 h-5" />
                    <span>Activée</span>
                  </span>
                ) : (
                  <span className="flex items-center space-x-2 text-gray-400">
                    <AlertCircle className="w-5 h-5" />
                    <span>Désactivée</span>
                  </span>
                )}
              </p>
            </div>
          </div>

          {template_path && (
            <div className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
              <div className="flex-shrink-0 mt-1 text-primary-dark">
                <FileText className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-500">Template Word</p>
                <p className="text-sm text-gray-900 font-mono break-all">{template_path}</p>
              </div>
            </div>
          )}

          {output_path && (
            <div className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg md:col-span-2">
              <div className="flex-shrink-0 mt-1 text-primary-dark">
                <FileText className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-500">Chemin de sortie</p>
                <p className="text-sm text-gray-900 font-mono break-all">{output_path}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Données de logs */}
      {log_data && (
        <div>
          <SectionTitle>Configuration des codes d'erreur</SectionTitle>

          {/* WTG OK */}
          {log_data.wtg_ok && log_data.wtg_ok.length > 0 && (
            <div className="mb-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h5 className="text-sm font-semibold text-green-900 mb-2 flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4" />
                  <span>Codes de fonctionnement normal</span>
                </h5>
                <div className="flex flex-wrap gap-2">
                  {log_data.wtg_ok.map((code, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-green-100 text-green-800 text-xs font-mono rounded-full"
                    >
                      {code}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Authorized Stop */}
          {log_data.authorized_stop && log_data.authorized_stop.length > 0 && (
            <div className="mb-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h5 className="text-sm font-semibold text-blue-900 mb-2 flex items-center space-x-2">
                  <AlertCircle className="w-4 h-4" />
                  <span>Arrêts autorisés</span>
                </h5>
                <div className="flex flex-wrap gap-2">
                  {log_data.authorized_stop.map((code, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-mono rounded-full"
                    >
                      {code}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Unauthorized Stop */}
          {log_data.unauthorized_stop && log_data.unauthorized_stop.length > 0 && (
            <div className="mb-4">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h5 className="text-sm font-semibold text-red-900 mb-2 flex items-center space-x-2">
                  <AlertCircle className="w-4 h-4" />
                  <span>Arrêts non autorisés (impactant disponibilité)</span>
                </h5>
                <div className="flex flex-wrap gap-2">
                  {log_data.unauthorized_stop.map((code, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-red-100 text-red-800 text-xs font-mono rounded-full"
                    >
                      {code}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {(!log_data.wtg_ok || log_data.wtg_ok.length === 0) &&
            (!log_data.authorized_stop || log_data.authorized_stop.length === 0) &&
            (!log_data.unauthorized_stop || log_data.unauthorized_stop.length === 0) && (
              <div className="text-center py-8 text-gray-500">
                <p>Aucune configuration de codes d'erreur définie.</p>
              </div>
            )}
        </div>
      )}
    </div>
  );
}
