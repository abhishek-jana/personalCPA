import { useState, useRef, useEffect } from 'react';
import { Send, Bot, Loader2, Sparkles } from 'lucide-react';
import { API_BASE_URL } from '../lib/api';

const Assistant = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: "Hello! I'm your Personal CPA. I've analyzed your latest transactions. How can I help you optimize your taxes today?" }
  ]);
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isThinking]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsThinking(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, use_rag: true })
      });
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', text: data.answer }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', text: "Sorry, I'm having trouble connecting to my local memory." }]);
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white border-l border-slate-200">
      <div className="p-6 border-b border-slate-100 bg-slate-50/30 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-indigo-100 text-indigo-600 rounded-lg flex items-center justify-center">
            <Bot size={18} />
          </div>
          <h3 className="font-black text-sm tracking-tight text-slate-800 uppercase">CPA Assistant</h3>
        </div>
        <Sparkles size={16} className="text-amber-400" />
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'} max-w-[85%]`}>
              <div className={`p-4 rounded-2xl text-sm leading-relaxed ${
                m.role === 'user' 
                ? 'bg-indigo-600 text-white rounded-tr-none shadow-md shadow-indigo-100' 
                : 'bg-slate-100 text-slate-800 rounded-tl-none border border-slate-200'
              }`}>
                {m.text}
              </div>
              <span className="text-[10px] font-bold text-slate-300 mt-2 uppercase tracking-widest">
                {m.role === 'user' ? 'You' : 'Assistant'}
              </span>
            </div>
          </div>
        ))}
        {isThinking && (
          <div className="flex justify-start">
            <div className="bg-slate-50 border border-slate-100 p-4 rounded-2xl rounded-tl-none flex items-center text-slate-400 text-sm italic">
              <Loader2 size={14} className="animate-spin mr-3 text-indigo-500" /> 
              Consulting local knowledge base...
            </div>
          </div>
        )}
      </div>

      <div className="p-6 bg-slate-50/50 border-t border-slate-100">
        <div className="relative group">
          <input 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask a question..."
            className="w-full bg-white border border-slate-200 rounded-2xl pl-4 pr-14 py-4 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
          />
          <button 
            onClick={handleSend} 
            className="absolute right-2 top-2 bottom-2 px-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors shadow-sm"
          >
            <Send size={18} />
          </button>
        </div>
        <p className="text-[10px] text-center text-slate-400 mt-4 font-medium">
          All data remains local on your machine.
        </p>
      </div>
    </div>
  );
};

export default Assistant;
