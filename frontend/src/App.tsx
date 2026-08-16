import { useState } from 'react'

export default function App() {
  const [activeTab, setActiveTab] = useState<'overview' | 'status'>('overview')

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
      {/* Header / Navbar */}
      <header className="border-b border-slate-800 bg-slate-950/50 backdrop-blur px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white">
            AI
          </div>
          <span className="text-xl font-bold tracking-tight text-white">Smart Campus Core</span>
        </div>
        <nav className="flex items-center space-x-4">
          <button 
            onClick={() => setActiveTab('overview')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'overview' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Overview
          </button>
          <button 
            onClick={() => setActiveTab('status')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'status' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            System Health
          </button>
        </nav>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6">
        {activeTab === 'overview' ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700/50">
              <h2 className="text-lg font-semibold text-blue-400 mb-2">FastAPI Backend</h2>
              <p className="text-sm text-slate-400">Connected to WebSocket Manager, PostgreSQL, and Redis Pub/Sub.</p>
            </div>
            <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700/50">
              <h2 className="text-lg font-semibold text-emerald-400 mb-2">AI Services</h2>
              <p className="text-sm text-slate-400">Campus RAG, Complaint Classification, and Risk Predictor ready.</p>
            </div>
            <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700/50">
              <h2 className="text-lg font-semibold text-purple-400 mb-2">Realtime Alerts</h2>
              <p className="text-sm text-slate-400">Role-based WebSocket broadcasting initialized.</p>
            </div>
          </div>
        ) : (
          <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700/50">
            <h2 className="text-xl font-bold mb-4">System Services</h2>
            <ul className="space-y-3">
              <li className="flex items-center justify-between border-b border-slate-700/50 pb-2">
                <span>API Endpoint (`/api/v1`)</span>
                <span className="text-emerald-400 text-sm font-medium">● Operational</span>
              </li>
              <li className="flex items-center justify-between border-b border-slate-700/50 pb-2">
                <span>WebSocket Endpoint (`/ws/role`)</span>
                <span className="text-emerald-400 text-sm font-medium">● Operational</span>
              </li>
              <li className="flex items-center justify-between pb-2">
                <span>Database Connection</span>
                <span className="text-emerald-400 text-sm font-medium">● Operational</span>
              </li>
            </ul>
          </div>
        )}
      </main>
    </div>
  )
}