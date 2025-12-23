import Dashboard from "./pages/Dashboard";
import { DataProvider } from "./contexts/DataContext";

const App = () => (
  <DataProvider>
    <Dashboard />
  </DataProvider>
);

export default App;
