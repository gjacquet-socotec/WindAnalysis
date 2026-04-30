import { useContext } from 'react';
import { WizardContext, type WizardContextValue } from '../wizard/WizardContext';

/**
 * Hook to access the Wizard context
 * Throws an error if used outside of WizardProvider
 */
export function useWizard(): WizardContextValue {
  const context = useContext(WizardContext);

  if (!context) {
    throw new Error('useWizard must be used within a WizardProvider');
  }

  return context;
}
