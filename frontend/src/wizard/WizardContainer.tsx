import { useWizard } from '../hooks/useWizard';
import { StepIndicator } from './components/StepIndicator';
import { Step1DataSource } from './components/Step1DataSource';
import { Step2ConfigReview } from './components/Step2ConfigReview';
import { Step3Results } from './components/Step3Results';
import { ErrorNotification } from '../components/ErrorNotification';

export function WizardContainer() {
  const { state, setError } = useWizard();

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-primary-dark text-white py-6 shadow-md">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold">Wind Turbine Analytics Wizard</h1>
          <p className="text-sm mt-1">Assistant d'analyse de performance d'éoliennes</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-[95%]">
        {/* Step Indicator - Centered */}
        <div className="max-w-4xl mx-auto">
          <StepIndicator currentStep={state.currentStep} />
        </div>

        {/* Step Content - Centered */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          {state.currentStep === 'dataSource' && <Step1DataSource />}
          {state.currentStep === 'configReview' && <Step2ConfigReview />}
          {state.currentStep === 'results' && <Step3Results />}
        </div>
      </main>

      {/* Error Notification */}
      {state.error && (
        <ErrorNotification
          message={state.error}
          onClose={() => setError(null)}
        />
      )}
    </div>
  );
}
