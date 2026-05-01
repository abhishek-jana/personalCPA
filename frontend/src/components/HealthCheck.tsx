import { useEffect, useState } from 'react';
import { AlertTriangle, RefreshCw, CheckCircle2 } from 'lucide-react';
import { API_BASE_URL } from '../lib/api';

interface HealthStatus {
  status: 'ok' | 'error';
  ollama: { status: string; message?: string };
  vss: { status: string; message?: string };
  missing_critical: string[];
  missing_optional: string[];
}

const HealthCheck = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const checkHealth = () => {
    setLoading(true);
    fetch(`${API_BASE_URL}/health`)
      .then(res => res.json())
      .then(data => {
        setHealth(data);
        setLoading(false);
      })
      .catch(() => {
        setHealth({
          status: 'error',
          ollama: { status: 'error', message: 'Backend connection failed' },
          vss: { status: 'error', message: 'Backend connection failed' },
          missing_critical: [],
          missing_optional: []
        });
        setLoading(false);
      });
  };

  useEffect(() => {
    checkHealth();
  }, []);

  if (loading) return null;
  if (!health) return null;

  const isCritical = health.status === 'error';
  const hasOptional = health.missing_optional.length > 0;

  if (!isCritical && !hasOptional) return null;

  return (
    <div className={`mb-8 p-6 border-2 rounded-2xl animate-in slide-in-from-top duration-500 ${
      isCritical ? 'bg-rose-50 border-rose-200' : 'bg-amber-50 border-amber-200'
    }`}>
      <div className="flex items-start space-x-4">
        <div className={`p-3 rounded-xl shadow-sm ${
          isCritical ? 'bg-white text-rose-600' : 'bg-white text-amber-600'
        }`}>
          {isCritical ? <AlertTriangle size={24} /> : <CheckCircle2 size={24} />}
        </div>
        <div className="flex-1">
          <h3 className={`text-lg font-black uppercase tracking-tight ${
            isCritical ? 'text-rose-900' : 'text-amber-900'
          }`}>
            {isCritical ? 'System Dependencies Missing' : 'System Recommendations'}
          </h3>
          <p className={`text-sm mt-1 font-medium ${
            isCritical ? 'text-rose-700' : 'text-amber-700'
          }`}>
            {isCritical 
              ? 'Your Personal CPA is currently impaired. Please address the following critical issues:'
              : 'Your system is functional, but you might want to optimize your experience:'}
          </p>
          
          <ul className="mt-4 space-y-3">
            {isCritical && (
              <>
                {health.ollama.status === 'error' && (
                  <li className="flex items-center text-sm text-rose-800 bg-white/50 p-2 rounded-lg">
                    <span className="w-2 h-2 bg-rose-500 rounded-full mr-3"></span>
                    <strong>Ollama:</strong> {health.ollama.message}
                  </li>
                )}
                {health.vss.status === 'error' && (
                  <li className="flex items-center text-sm text-rose-800 bg-white/50 p-2 rounded-lg">
                    <span className="w-2 h-2 bg-rose-500 rounded-full mr-3"></span>
                    <strong>Memory (Vector DB):</strong> {health.vss.message}
                  </li>
                )}
                {health.missing_critical.map(m => (
                  <li key={m} className="flex flex-col text-sm text-rose-800 bg-white/50 p-3 rounded-lg">
                    <div className="flex items-center mb-2">
                      <span className="w-2 h-2 bg-rose-500 rounded-full mr-3"></span>
                      <strong>Critical Model Missing:</strong> {m}
                    </div>
                    <code className="bg-rose-100 px-2 py-1 rounded text-xs font-bold border border-rose-200 self-start ml-5">
                      ollama pull {m}
                    </code>
                  </li>
                ))}
              </>
            )}
            {hasOptional && (
              <li className="flex flex-col text-sm text-amber-800 bg-white/50 p-3 rounded-lg">
                <div className="flex items-center mb-2">
                  <span className="w-2 h-2 bg-amber-500 rounded-full mr-3"></span>
                  <strong>Optional Models (Fast/Expert):</strong>
                </div>
                <div className="flex flex-wrap gap-2 ml-5">
                  {health.missing_optional.map(m => (
                    <code key={m} className="bg-amber-100 px-2 py-1 rounded text-xs font-bold border border-amber-200">
                      ollama pull {m}
                    </code>
                  ))}
                </div>
              </li>
            )}
          </ul>
        </div>
        <button 
          onClick={checkHealth}
          className={`p-2 rounded-xl shadow-sm transition-colors bg-white ${
            isCritical ? 'text-rose-600 hover:bg-rose-100' : 'text-amber-600 hover:bg-amber-100'
          }`}
          title="Retry"
        >
          <RefreshCw size={20} />
        </button>
      </div>
    </div>
  );
};

export default HealthCheck;
