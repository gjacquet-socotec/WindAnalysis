import { WizardProvider } from "./wizard/WizardContext";
import { WizardContainer } from "./wizard/WizardContainer";

function App() {
  return (
    <WizardProvider>
      <WizardContainer />
    </WizardProvider>
  );
}

export default App;
