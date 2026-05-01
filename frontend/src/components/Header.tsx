import { DollarSign, TrendingUp, Activity } from 'lucide-react';
import MetricCard from './MetricCard';
import { useEffect, useState } from 'react';

const Header = () => {
  const [pulse, setPulse] = useState({ tax_estimate: 0, savings_rate: '0%', total_spent: 0 });

  useEffect(() => {
    fetch('http://127.0.0.1:8000/dashboard/pulse')
      .then(res => res.json())
      .then(data => setPulse(data))
      .catch(console.error);
  }, []);

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
      <div className="flex space-x-4">
        <MetricCard label="Tax Estimate" value={`$${pulse.tax_estimate.toLocaleString()}`} icon={<DollarSign size={18} />} color="text-emerald-600" />
        <MetricCard label="Savings Rate" value={pulse.savings_rate} icon={<TrendingUp size={18} />} color="text-blue-600" />
        <MetricCard label="Total Spent" value={`$${pulse.total_spent.toLocaleString()}`} icon={<Activity size={18} />} color="text-rose-600" />
      </div>
    </header>
  );
};

export default Header;
