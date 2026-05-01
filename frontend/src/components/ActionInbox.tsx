import { AlertCircle, Tag, FileText, CheckCircle2 } from 'lucide-react';
import { useEffect, useState } from 'react';

const ActionInbox = () => {
  const [actions, setActions] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/dashboard/inbox')
      .then(res => res.json())
      .then(data => setActions(data))
      .catch(console.error);
  }, []);

  if (actions.length === 0) {
    return (
      <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm flex flex-col items-center justify-center text-center">
        <div className="w-12 h-12 bg-emerald-50 text-emerald-500 rounded-full flex items-center justify-center mb-4">
          <CheckCircle2 size={24} />
        </div>
        <h3 className="text-lg font-semibold text-slate-900">All clear!</h3>
        <p className="text-sm text-slate-500">No pending tasks for your attention.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {actions.map((action, i) => (
        <div key={i} className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm flex items-start space-x-4 hover:border-indigo-200 transition-colors cursor-pointer group">
          <div className={`p-3 rounded-xl ${action.type === 'categorization' ? 'bg-amber-50 text-amber-600' : 'bg-rose-50 text-rose-600'}`}>
            {action.type === 'categorization' ? <Tag size={20} /> : <AlertCircle size={20} />}
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">{action.message}</h3>
            <p className="text-xs text-slate-500 mt-1">Requires manual review to improve tax accuracy.</p>
          </div>
          <button className="bg-slate-50 text-slate-400 px-3 py-1 rounded-lg text-xs font-bold group-hover:bg-indigo-600 group-hover:text-white transition-all">
            GO
          </button>
        </div>
      ))}
    </div>
  );
};

export default ActionInbox;
