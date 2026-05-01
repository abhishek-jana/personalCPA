import { ReactNode } from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  icon: ReactNode;
  color: string;
}

const MetricCard = ({ label, value, icon, color }: MetricCardProps) => (
  <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100 flex items-center space-x-4 min-w-[180px]">
    <div className={`p-3 rounded-lg bg-slate-50 ${color}`}>
      {icon}
    </div>
    <div>
      <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{label}</p>
      <p className="text-lg font-bold text-slate-900">{value}</p>
    </div>
  </div>
);

export default MetricCard;
