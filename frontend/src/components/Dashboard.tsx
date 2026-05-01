import ActionInbox from './ActionInbox';
import TransactionTable from './TransactionTable';
import KnowledgeBase from './KnowledgeBase';

const Dashboard = () => (
  <div className="space-y-12 animate-in fade-in duration-500 pb-20">
    <section>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-black tracking-tight text-slate-800">Guardian Inbox</h2>
        <span className="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full text-xs font-black uppercase tracking-tighter">
          Task Driven
        </span>
      </div>
      <ActionInbox />
    </section>

    <section>
      <KnowledgeBase />
    </section>

    <section>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-black tracking-tight text-slate-800">Recent Transactions</h2>
        <button className="text-xs font-bold text-indigo-600 hover:text-indigo-800 uppercase tracking-widest transition-colors">
          View Full Ledger
        </button>
      </div>
      <TransactionTable />
    </section>
  </div>
);

export default Dashboard;
