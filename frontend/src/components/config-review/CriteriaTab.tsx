import type { ValidationCriteria, CriterionValue } from '../../types/config';
import { CheckCircle2, Target, Info } from 'lucide-react';

interface CriteriaTabProps {
  criteria: ValidationCriteria;
  workflowType: 'runtest' | 'scada';
}

interface CriterionItemProps {
  label: string;
  criterion: CriterionValue;
}

function CriterionItem({ label, criterion }: CriterionItemProps) {
  return (
    <div className="flex items-start space-x-3 p-4 border border-gray-200 rounded-lg hover:border-primary-dark transition-colors">
      <div className="flex-shrink-0 mt-1">
        <CheckCircle2 className="w-5 h-5 text-green-600" />
      </div>
      <div className="flex-1">
        <div className="flex items-baseline justify-between mb-2">
          <h4 className="text-sm font-semibold text-gray-900">{label}</h4>
          <span className="text-lg font-bold text-primary-dark">
            {criterion.value} <span className="text-sm font-normal text-gray-600">{criterion.unit}</span>
          </span>
        </div>

        {/* Description from config */}
        {criterion.description && (
          <p className="text-xs text-gray-600 mb-1">
            <span className="font-medium">Description:</span> {criterion.description}
          </p>
        )}

        {/* Specification from config */}
        {criterion.specification !== null && criterion.specification !== undefined && (
          <div className="flex items-start space-x-1 text-xs text-blue-700 bg-blue-50 px-2 py-1 rounded">
            <Info className="w-3 h-3 mt-0.5 flex-shrink-0" />
            <span>
              <span className="font-medium">Spécification:</span>{' '}
              {Array.isArray(criterion.specification)
                ? criterion.specification.join(' - ')
                : criterion.specification}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

export function CriteriaTab({ criteria, workflowType }: CriteriaTabProps) {
  const runTestCriteria = [
    { key: 'consecutive_hours', label: 'Heures consécutives' },
    { key: 'cut_in_to_cut_out', label: 'Cut-In à Cut-Out' },
    { key: 'nominal_power_hours', label: 'Heures à puissance nominale' },
    { key: 'local_restarts', label: 'Redémarrages locaux' },
    { key: 'availability', label: 'Disponibilité' },
  ];

  const scadaCriteria = [
    { key: 'eba_cut_in_cut_out', label: 'EBA Cut-In/Cut-Out' },
    { key: 'eba_manufacturer', label: 'EBA Constructeur' },
    { key: 'data_availability', label: 'Disponibilité des données' },
  ];

  const criteriaToDisplay = workflowType === 'runtest' ? runTestCriteria : scadaCriteria;
  const criteriaEntries = Object.entries(criteria);

  return (
    <div>
      <div className="flex items-center space-x-2 mb-4">
        <Target className="w-6 h-6 text-primary-dark" />
        <h3 className="text-lg font-bold text-gray-900">
          Critères de validation {workflowType === 'runtest' ? 'RunTest' : 'SCADA'}
        </h3>
      </div>

      {criteriaEntries.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {criteriaToDisplay.map((item) => {
            const criterion = criteria[item.key as keyof ValidationCriteria];
            if (!criterion) return null;

            return (
              <CriterionItem
                key={item.key}
                label={item.label}
                criterion={criterion}
              />
            );
          })}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <p>Aucun critère de validation défini dans la configuration.</p>
        </div>
      )}
    </div>
  );
}
