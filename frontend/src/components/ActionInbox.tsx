import { AlertCircle, Tag, CheckCircle2, ShieldAlert, ArrowRight } from 'lucide-react';
import { useEffect, useState } from 'react';
import { API_BASE_URL } from '../lib/api';

interface Action {
  type: 'categorization' | 'audit' | 'other';
  message: string;
  count: number;
}

interface Anomaly {
    filename: string;
    collection: string;
    reason: string;
}

const ActionInbox = () => {
  const [actions, setActions] = useState<Action[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [isAuditing, setIsAuditing] = useState(false);

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
        window.location.reload(); 
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRunAudit = async (action: Action) => {
    const colName = action.message.split(' ').pop(); // Extracting collection name from message
    if (!colName) return;

    setIsAuditing(true);
    try {
        const res = await fetch(`${API_BASE_URL}/audit/${encodeURIComponent(colName)}`, { method: 'POST' });
        const data = await res.json();
        setAnomalies(data);
    } catch (err) {
        console.error(err);
    } finally {
        setIsAuditing(false);
    }
  };

  const handleMoveFile = async (anomaly: Anomaly, target: string) => {
      try {
          const res = await fetch(`${API_BASE_URL}/documents/move`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                  filename: anomaly.filename,
                  from_collection: anomaly.collection,
                  to_collection: target
              })
          });
          if (res.ok) {
              setAnomalies(anomalies.filter(a => a.filename !== anomaly.filename));
              fetchActions();
          }
      } catch (err) {
          console.error(err);
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
    <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {actions.map((action, i) => (
            <div key={i} className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm flex items-start space-x-4 hover:border-indigo-200 transition-colors cursor-pointer group">
            <div className={`p-3 rounded-xl ${
                action.type === 'categorization' ? 'bg-amber-50 text-amber-600' : 
                action.type === 'audit' ? 'bg-rose-50 text-rose-600' : 'bg-slate-50 text-slate-600'
            }`}>
                {action.type === 'categorization' ? <Tag size={20} /> : 
                action.type === 'audit' ? <ShieldAlert size={20} /> : <AlertCircle size={20} />}
            </div>
            <div className="flex-1">
                <h3 className="font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">{action.message}</h3>
                <p className="text-xs text-slate-500 mt-1">
                    {action.type === 'categorization' ? 'Requires manual review to improve tax accuracy.' : 
                    action.type === 'audit' ? 'AI Auditor detected files that may be in the wrong folder.' : 'Action required.'}
                </p>
            </div>
            <div className="flex flex-col space-y-2">
                <button 
                    onClick={() => action.type === 'audit' ? handleRunAudit(action) : null}
                    className="bg-slate-50 text-slate-400 px-3 py-1 rounded-lg text-xs font-bold group-hover:bg-indigo-600 group-hover:text-white transition-all"
                >
                    {isAuditing ? '...' : 'GO'}
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

        {anomalies.length > 0 && (
            <div className="bg-white rounded-2xl border-2 border-rose-100 shadow-xl overflow-hidden animate-in slide-in-from-bottom-4 duration-300">
                <div className="bg-rose-50 p-4 border-b border-rose-100 flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-rose-700">
                        <ShieldAlert size={18} />
                        <span className="font-black uppercase tracking-tighter text-xs">AI Audit Anomalies</span>
                    </div>
                    <button onClick={() => setAnomalies([])} className="text-rose-400 hover:text-rose-600 font-bold text-xs">DISMISS</button>
                </div>
                <div className="divide-y divide-slate-50">
                    {anomalies.map((a, i) => (
                        <div key={i} className="p-4 flex items-center justify-between">
                            <div className="flex-1">
                                <p className="text-sm font-bold text-slate-900">{a.filename}</p>
                                <p className="text-xs text-rose-500 font-medium italic mt-0.5">{a.reason}</p>
                            </div>
                            <div className="flex items-center space-x-2">
                                <button 
                                    onClick={() => handleMoveFile(a, 'General')}
                                    className="flex items-center space-x-1.5 bg-slate-900 text-white px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest hover:bg-indigo-600 transition-all"
                                >
                                    <span>Move to General</span>
                                    <ArrowRight size={12} />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        )}
    </div>
  );
};

export default ActionInbox;
