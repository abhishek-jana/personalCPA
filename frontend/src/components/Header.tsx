import { DollarSign, TrendingUp, Activity, BrainCircuit } from 'lucide-react';
import MetricCard from './MetricCard';
import { useEffect, useState } from 'react';
import { API_BASE_URL } from '../lib/api';

interface Config {
  backend: string;
  model: string;
  model_type: string;
  available_types: string[];
}

const Header = () => {
  const [pulse, setPulse] = useState({ tax_estimate: 0, savings_rate: '0%', total_spent: 0 });
  const [config, setConfig] = useState<Config | null>(null);
  const [isSwitching, setIsSwitching] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE_URL}/dashboard/pulse`)
      .then(res => res.json())
      .then(data => setPulse(data))
      .catch(console.error);

    fetch(`${API_BASE_URL}/config`)
      .then(res => res.json())
      .then(data => setConfig(data))
      .catch(console.error);
  }, []);

  const handleModelSwitch = async (type: string) => {
    if (!config || isSwitching || type === config.model_type) return;
    
    setIsSwitching(true);
    try {
      const response = await fetch(`${API_BASE_URL}/config/model`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_type: type })
      });
      const data = await response.json();
      if (data.status === 'switched') {
        setConfig(prev => prev ? { ...prev, model_type: data.new_type, model: data.new_model } : null);
      }
    } catch (err) {
      console.error('Failed to switch model:', err);
    } finally {
      setIsSwitching(false);
    }
  };

  return (
    <header className="h-20 bg-white border-b border-slate-200 flex items-center justify-between px-8 shadow-sm z-10">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-indigo-200 shadow-lg">
          <DollarSign className="text-white" size={24} />
        </div>
        <div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">
            Personal Local CPA
          </h1>
          <p className="text-[10px] text-slate-400 font-medium uppercase tracking-widest">Privacy First Finance</p>
        </div>
      </div>

      <div className="flex items-center space-x-6">
        {config && (
          <div className="flex items-center bg-slate-50 border border-slate-100 rounded-xl p-1.5 space-x-1">
            {config.available_types.map(type => (
              <button
                key={type}
                onClick={() => handleModelSwitch(type)}
                disabled={isSwitching}
                className={`px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-tight transition-all ${
                  config.model_type === type 
                    ? 'bg-white text-indigo-600 shadow-sm' 
                    : 'text-slate-400 hover:text-slate-600'
                } ${isSwitching ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {type}
              </button>
            ))}
            <div className="ml-2 pl-2 border-l border-slate-200 flex items-center text-slate-400">
              <BrainCircuit size={14} className={isSwitching ? 'animate-pulse text-indigo-500' : ''} />
              <span className="ml-1.5 text-[9px] font-bold truncate max-w-[80px]">{config.model}</span>
            </div>
          </div>
        )}

        <div className="flex space-x-3">
          <MetricCard label="Tax Estimate" value={`$${pulse.tax_estimate.toLocaleString()}`} icon={<DollarSign size={18} />} color="text-emerald-600" />
          <MetricCard label="Savings Rate" value={pulse.savings_rate} icon={<TrendingUp size={18} />} color="text-blue-600" />
          <MetricCard label="Total Spent" value={`$${pulse.total_spent.toLocaleString()}`} icon={<Activity size={18} />} color="text-rose-600" />
        </div>
      </div>
    </header>
  );
};

export default Header;
