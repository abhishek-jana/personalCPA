import { useEffect, useState } from 'react';
import { Folder, FileText, Upload, Plus, Search } from 'lucide-react';

const KnowledgeBase = () => {
  const [collections, setCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [newCollectionName, setNewCollectionName] = useState("");

  useEffect(() => {
    fetchCollections();
  }, []);

  const fetchCollections = () => {
    fetch('http://127.0.0.1:8000/collections')
      .then(res => res.json())
      .then(data => {
        setCollections(data);
        if (data.length > 0 && !selectedCollection) {
          setSelectedCollection(data[0]);
        }
      })
      .catch(console.error);
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || !e.target.files[0]) return;
    
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('collection', selectedCollection || 'General');

    setIsUploading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/documents/upload', {
        method: 'POST',
        body: formData,
      });
      if (res.ok) {
        fetchCollections();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleCreateCollection = () => {
    if (!newCollectionName.strip()) return;
    if (!collections.includes(newCollectionName)) {
      setCollections([...collections, newCollectionName]);
      setSelectedCollection(newCollectionName);
    }
    setNewCollectionName("");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-black tracking-tight text-slate-800">Knowledge Base</h2>
        <div className="flex items-center space-x-2">
            <input 
                type="text" 
                placeholder="New folder name..."
                value={newCollectionName}
                onChange={(e) => setNewCollectionName(e.target.value)}
                className="text-xs px-3 py-1 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button 
                onClick={handleCreateCollection}
                className="bg-indigo-600 text-white p-1.5 rounded-lg hover:bg-indigo-700 transition-colors"
            >
                <Plus size={16} />
            </button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-6">
        {/* Sidebar / Folder List */}
        <div className="col-span-1 space-y-2">
          {collections.map(c => (
            <button
              key={c}
              onClick={() => setSelectedCollection(c)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-bold transition-all ${
                selectedCollection === c 
                ? 'bg-indigo-600 text-white shadow-md' 
                : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-100'
              }`}
            >
              <Folder size={18} />
              <span className="truncate">{c}</span>
            </button>
          ))}
          {collections.length === 0 && (
            <p className="text-xs text-slate-400 italic p-4">No folders yet.</p>
          )}
        </div>

        {/* Content Area */}
        <div className="col-span-3 bg-white rounded-2xl border border-slate-100 shadow-sm p-8 min-h-[400px] flex flex-col">
          {selectedCollection ? (
            <>
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h3 className="text-xl font-black text-slate-900">{selectedCollection}</h3>
                  <p className="text-xs text-slate-500 mt-1">Ground the Assistant in this context.</p>
                </div>
                <label className="cursor-pointer bg-slate-900 text-white px-4 py-2 rounded-xl text-xs font-bold hover:bg-slate-800 transition-all flex items-center space-x-2">
                  <Upload size={14} />
                  <span>{isUploading ? 'Uploading...' : 'Upload Document'}</span>
                  <input type="file" className="hidden" onChange={handleUpload} disabled={isUploading} />
                </label>
              </div>

              <div className="flex-1 flex flex-col items-center justify-center text-center space-y-4">
                <div className="w-16 h-16 bg-slate-50 text-slate-300 rounded-2xl flex items-center justify-center">
                  <FileText size={32} />
                </div>
                <div>
                  <h4 className="font-bold text-slate-800">Folder context ready</h4>
                  <p className="text-sm text-slate-500 max-w-xs mx-auto">
                    The Assistant will automatically use documents in this folder when you ask related questions.
                  </p>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center">
                <Search size={48} className="text-slate-100 mb-4" />
                <p className="text-slate-400 font-medium">Select a folder to view documents</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBase;
