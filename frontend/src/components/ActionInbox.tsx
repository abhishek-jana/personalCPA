import { AlertCircle, Tag, CheckCircle2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { API_BASE_URL } from '../lib/api';

interface Action {
  type: 'categorization' | 'other';
  message: string;
  count: number;
}

const ActionInbox = () => {
  const [actions, setActions] = useState<Action[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    fetchActions();
  }, []);

  const fetchActions = () => {
    fetch(`${API_BASE_URL}/dashboard/inbox`)
      .then(res => res.json())
      .then(data => setActions(data))
      .catch(console.error);
  };

  const handleAutoCategorize = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsProcessing(true);
    try {
      const res = await fetch(`${API_BASE_URL}/transactions/categorize`, { method: 'POST' });
      if (res.ok) {
        fetchActions();
        // Trigger a global refresh to update the transaction table
        window.location.reload(); 
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

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
          <div className="flex flex-col space-y-2">
            <button className="bg-slate-50 text-slate-400 px-3 py-1 rounded-lg text-xs font-bold group-hover:bg-indigo-600 group-hover:text-white transition-all">
                GO
            </button>
            {action.type === 'categorization' && (
                <button 
                    onClick={handleAutoCategorize}
                    disabled={isProcessing}
                    className="bg-emerald-50 text-emerald-600 px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest hover:bg-emerald-600 hover:text-white transition-all disabled:opacity-50"
                >
                    {isProcessing ? '...' : 'Auto'}
                </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ActionInbox;
