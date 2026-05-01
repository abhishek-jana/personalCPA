import Header from './components/Header';
import Dashboard from './components/Dashboard';
import Assistant from './components/Assistant';

function App() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      <Header />
      <main className="flex-1 flex overflow-hidden">
        <div className="w-[70%] overflow-y-auto p-6 border-r border-slate-200">
          <Dashboard />
        </div>
        <div className="w-[30%] bg-white flex flex-col h-full shadow-lg">
          <Assistant />
        </div>
      </main>
    </div>
  );
}

export default App;
