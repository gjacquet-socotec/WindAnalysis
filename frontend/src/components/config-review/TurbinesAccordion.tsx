import type { TurbineConfiguration } from '../../types/config';
import { Accordion, type AccordionItem } from '../shared/Accordion';
import { Wind, FileText, Calendar, Database } from 'lucide-react';

interface TurbinesAccordionProps {
  turbines: TurbineConfiguration[];
}

interface DetailRowProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
}

function DetailRow({ label, value, icon }: DetailRowProps) {
  return (
    <div className="flex items-start space-x-2 py-2">
      {icon && <div className="flex-shrink-0 mt-0.5 text-gray-500">{icon}</div>}
      <div className="flex-1 grid grid-cols-2 gap-4">
        <span className="text-sm font-medium text-gray-600">{label}:</span>
        <span className="text-sm text-gray-900 break-all">{value}</span>
      </div>
    </div>
  );
}

function TurbineContent({ turbine }: { turbine: TurbineConfiguration }) {
  const generalInfo = turbine.general_information;

  return (
    <div className="space-y-4">
      {/* Basic Info */}
      <div>
        <h5 className="text-sm font-bold text-gray-700 mb-2 flex items-center space-x-2">
          <Wind className="w-4 h-4" />
          <span>Informations générales</span>
        </h5>
        <div className="space-y-1 bg-gray-50 p-3 rounded">
          <DetailRow label="ID Turbine" value={turbine.turbine_id} />
          <DetailRow label="Modèle" value={generalInfo.model} />
          <DetailRow label="Puissance nominale" value={`${generalInfo.nominal_power} MW`} />
          <DetailRow label="Constructeur" value={generalInfo.constructor} />
        </div>
      </div>

      {/* Files */}
      <div>
        <h5 className="text-sm font-bold text-gray-700 mb-2 flex items-center space-x-2">
          <FileText className="w-4 h-4" />
          <span>Fichiers de données</span>
        </h5>
        <div className="space-y-1 bg-gray-50 p-3 rounded">
          <DetailRow label="Données d'opération" value={generalInfo.path_operation_data} />
          <DetailRow label="Logs" value={generalInfo.path_log_data} />
          {generalInfo.path_guaranteed_power_curve && (
            <DetailRow label="Courbe de puissance garantie" value={generalInfo.path_guaranteed_power_curve} />
          )}
        </div>
      </div>

      {/* Test Period */}
      <div>
        <h5 className="text-sm font-bold text-gray-700 mb-2 flex items-center space-x-2">
          <Calendar className="w-4 h-4" />
          <span>Période de test</span>
        </h5>
        <div className="space-y-1 bg-gray-50 p-3 rounded">
          <DetailRow label="Début" value={turbine.test_start} />
          <DetailRow label="Fin" value={turbine.test_end} />
        </div>
      </div>

      {/* Mapping Operation Data */}
      <div>
        <h5 className="text-sm font-bold text-gray-700 mb-2 flex items-center space-x-2">
          <Database className="w-4 h-4" />
          <span>Mapping - Données d'opération</span>
        </h5>
        <div className="bg-gray-50 p-3 rounded max-h-60 overflow-y-auto">
          <div className="space-y-1 text-xs">
            {Object.entries(turbine.mapping_operation_data || {}).map(([key, value]) => (
              <div key={key} className="flex border-b border-gray-200 py-1.5">
                <span className="font-mono text-gray-600 w-48 flex-shrink-0">{key}:</span>
                <span className="font-mono text-gray-900 break-all">
                  {value === null || value === '' ? <em className="text-gray-400">null</em> : value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Mapping Log Data */}
      <div>
        <h5 className="text-sm font-bold text-gray-700 mb-2 flex items-center space-x-2">
          <Database className="w-4 h-4" />
          <span>Mapping - Données de logs</span>
        </h5>
        <div className="bg-gray-50 p-3 rounded">
          <div className="space-y-1 text-xs">
            {Object.entries(turbine.mapping_log_data || {}).map(([key, value]) => (
              <div key={key} className="flex border-b border-gray-200 py-1.5">
                <span className="font-mono text-gray-600 w-32 flex-shrink-0">{key}:</span>
                <span className="font-mono text-gray-900">
                  {Array.isArray(value) ? (
                    <span className="text-blue-700">[{value.join(', ')}]</span>
                  ) : (
                    value
                  )}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export function TurbinesAccordion({ turbines }: TurbinesAccordionProps) {
  if (!turbines || turbines.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Wind className="w-12 h-12 mx-auto mb-2 text-gray-400" />
        <p>Aucune turbine configurée.</p>
      </div>
    );
  }

  const accordionItems: AccordionItem[] = turbines.map((turbineConfig) => ({
    id: turbineConfig.turbine_id,
    title: `${turbineConfig.turbine_id} - ${turbineConfig.general_information.model}`,
    content: <TurbineContent turbine={turbineConfig} />,
  }));

  return (
    <div>
      <h3 className="text-lg font-bold text-gray-900 mb-4">
        Configuration des turbines ({turbines.length})
      </h3>
      <Accordion items={accordionItems} defaultOpen={[turbines[0].turbine_id]} allowMultiple={true} />
    </div>
  );
}
