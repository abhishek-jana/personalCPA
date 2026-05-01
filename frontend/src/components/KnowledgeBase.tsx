import { useEffect, useState } from 'react';
import { Folder, FileText, Upload, Plus, Search, Loader2 } from 'lucide-react';
import { API_BASE_URL } from '../lib/api';

interface CollectionDocument {
  filename: string;
  chunks: number;
}

const KnowledgeBase = () => {
  const [collections, setCollections] = useState<string[]>([]);
  const [selectedCollection, setSelectedCollection] = useState<string | null>(null);
  const [documents, setDocuments] = useState<CollectionDocument[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoadingDocs, setIsLoadingDocs] = useState(false);
  const [newCollectionName, setNewCollectionName] = useState("");

  useEffect(() => {
    fetchCollections();
  }, []);

  useEffect(() => {
    if (selectedCollection) {
      fetchDocuments(selectedCollection);
    }
  }, [selectedCollection]);

  const fetchCollections = () => {
    fetch(`${API_BASE_URL}/collections`)
      .then(res => res.json())
      .then(data => {
        setCollections(data);
        if (data.length > 0 && !selectedCollection) {
          setSelectedCollection(data[0]);
        }
      })
      .catch(console.error);
  };

  const fetchDocuments = (collectionName: string) => {
    setIsLoadingDocs(true);
    fetch(`${API_BASE_URL}/collections/${encodeURIComponent(collectionName)}/documents`)
      .then(res => res.json())
      .then(data => setDocuments(data))
      .catch(console.error)
      .finally(() => setIsLoadingDocs(false));
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || !e.target.files[0] || !selectedCollection) return;
    
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('collection', selectedCollection);

    setIsUploading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/documents/upload`, {
        method: 'POST',
        body: formData,
      });
      if (res.ok) {
        fetchDocuments(selectedCollection);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleCreateCollection = async () => {
    const name = newCollectionName.trim();
    if (!name) return;
    
    try {
        const res = await fetch(`${API_BASE_URL}/collections`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        if (res.ok) {
            setNewCollectionName("");
            fetchCollections();
            setSelectedCollection(name);
        }
    } catch (err) {
        console.error(err);
    }
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
                onKeyDown={(e) => e.key === 'Enter' && handleCreateCollection()}
                className="text-xs px-3 py-2 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 w-48"
            />
            <button 
                onClick={handleCreateCollection}
                className="bg-indigo-600 text-white p-2 rounded-xl hover:bg-indigo-700 transition-colors shadow-sm"
            >
                <Plus size={18} />
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
            <div className="p-8 border-2 border-dashed border-slate-200 rounded-2xl text-center">
                <p className="text-xs text-slate-400 italic">No folders yet.</p>
            </div>
          )}
        </div>

        {/* Content Area */}
        <div className="col-span-3 bg-white rounded-2xl border border-slate-100 shadow-sm min-h-[400px] flex flex-col overflow-hidden">
          {selectedCollection ? (
            <>
              <div className="p-6 border-b border-slate-50 bg-slate-50/30 flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-black text-slate-900">{selectedCollection}</h3>
                  <p className="text-xs text-slate-500 mt-1">Grounding context for your CPA Assistant.</p>
                </div>
                <label className="cursor-pointer bg-slate-900 text-white px-5 py-2.5 rounded-xl text-xs font-bold hover:bg-slate-800 transition-all flex items-center space-x-2 shadow-sm">
                  <Upload size={14} />
                  <span>{isUploading ? 'Ingesting...' : 'Upload to Folder'}</span>
                  <input type="file" className="hidden" onChange={handleUpload} disabled={isUploading} />
                </label>
              </div>

              <div className="flex-1 overflow-y-auto p-6">
                {isLoadingDocs ? (
                  <div className="h-full flex items-center justify-center text-slate-400">
                    <Loader2 className="animate-spin mr-2" size={20} />
                    <span className="text-sm font-medium">Loading documents...</span>
                  </div>
                ) : documents.length > 0 ? (
                  <div className="grid grid-cols-1 gap-3">
                    {documents.map((doc, i) => (
                      <div key={i} className="flex items-center justify-between p-4 rounded-xl border border-slate-100 hover:border-indigo-100 hover:bg-indigo-50/20 transition-all group">
                        <div className="flex items-center space-x-4">
                          <div className="w-10 h-10 bg-slate-50 text-slate-400 rounded-lg flex items-center justify-center group-hover:bg-white group-hover:text-indigo-500 transition-colors">
                            <FileText size={20} />
                          </div>
                          <div>
                            <p className="text-sm font-bold text-slate-900">{doc.filename}</p>
                            <p className="text-[10px] text-slate-400 uppercase font-black tracking-widest">{doc.chunks} Semantic Chunks</p>
                          </div>
                        </div>
                        <div className="bg-emerald-50 text-emerald-600 px-3 py-1 rounded-full text-[10px] font-bold">
                            READY
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-center space-y-4">
                    <div className="w-20 h-20 bg-slate-50 text-slate-200 rounded-3xl flex items-center justify-center">
                      <FileText size={40} />
                    </div>
                    <div>
                      <h4 className="font-bold text-slate-400">This folder is empty</h4>
                      <p className="text-xs text-slate-400 max-w-[200px] mx-auto mt-1">
                        Upload documents to give the Assistant context for this category.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-12">
                <div className="w-24 h-24 bg-slate-50 rounded-full flex items-center justify-center mb-6">
                    <Search size={40} className="text-slate-200" />
                </div>
                <h3 className="text-lg font-bold text-slate-900">Select or Create a Folder</h3>
                <p className="text-sm text-slate-500 max-w-xs mx-auto mt-2">
                    Organize your documents into collections to help the Assistant find exactly what it needs.
                </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBase;
