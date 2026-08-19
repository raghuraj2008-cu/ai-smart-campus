import React, { useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { fetchComplaints, createComplaint } from '../services/api';

export default function Dashboard({ onLogout }) {
  const token = localStorage.getItem('access_token');
  const [complaints, setComplaints] = useState([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('FACILITY');
  const [loading, setLoading] = useState(false);
  const [filterStatus, setFilterStatus] = useState('ALL');

  const { messages, isConnected } = useWebSocket(token);

  // Load existing complaints on mount
  useEffect(() => {
    fetchComplaints()
      .then((data) => setComplaints(data || []))
      .catch((err) => console.error('Failed to load tickets:', err));
  }, []);

  // Sync incoming real-time events
  useEffect(() => {
    if (!messages.length) return;
    const latest = messages[0];

    if (latest.event === 'COMPLAINT_CREATED' || latest.type === 'NEW_COMPLAINT') {
      const newItem = latest.data || latest.payload;
      setComplaints((prev) => [newItem, ...prev.filter((c) => c.id !== newItem.id)]);
      console.log('🔔 New Incident Dispatched:', newItem.title);
    } else if (
      latest.event === 'COMPLAINT_STATUS_UPDATED' || 
      latest.event === 'STATUS_UPDATED' || 
      latest.type === 'STATUS_UPDATE'
    ) {
      const updatedItem = latest.data || latest.payload;
      setComplaints((prev) =>
        prev.map((c) => (c.id === updatedItem.id ? { ...c, status: updatedItem.status } : c))
      );
    }
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) return;
    setLoading(true);
    try {
      await createComplaint({ title, description, category });
      setTitle('');
      setDescription('');
    } catch (err) {
      alert('Failed to submit incident');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Update Status Action
  const handleUpdateStatus = async (id, newStatus) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/complaints/${id}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: newStatus })
      });
      if (!response.ok) throw new Error('Failed to update status');
    } catch (err) {
      console.error('Status update error:', err);
      alert('Failed to update ticket status.');
    }
  };

  // Filtered view logic
  const displayedComplaints = complaints.filter((item) => {
    if (filterStatus === 'ALL') return true;
    return item.status === filterStatus;
  });

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '24px', fontFamily: 'sans-serif' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ margin: 0 }}>Smart Campus Control Center</h1>
          <span style={{ fontSize: '14px', color: isConnected ? '#10B981' : '#EF4444' }}>
            ● {isConnected ? 'Live Stream Active' : 'Connecting...'}
          </span>
        </div>
        {onLogout && (
          <button onClick={onLogout} style={{ padding: '8px 16px', cursor: 'pointer', background: '#334155', color: '#fff', border: 'none', borderRadius: '4px' }}>
            Sign Out
          </button>
        )}
      </header>

      <section style={{ background: '#f8fafc', padding: '20px', borderRadius: '8px', marginBottom: '32px' }}>
        <h3 style={{ marginTop: 0 }}>Report Campus Issue</h3>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <input
            type="text"
            placeholder="Issue Title (e.g., Severe electric spark in Physics Lab)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            style={{ padding: '10px', fontSize: '14px', border: '1px solid #cbd5e1', borderRadius: '4px' }}
          />
          <textarea
            placeholder="Detailed description of the issue..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            rows={2}
            style={{ padding: '10px', fontSize: '14px', border: '1px solid #cbd5e1', borderRadius: '4px' }}
          />
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              style={{ padding: '10px', fontSize: '14px', border: '1px solid #cbd5e1', borderRadius: '4px' }}
            >
              <option value="FACILITY">Facility & Maintenance</option>
              <option value="ACADEMIC">Academic & IT Lab</option>
              <option value="HOSTEL">Hostel & Housing</option>
              <option value="SECURITY">Security & Safety</option>
            </select>
            <button
              type="submit"
              disabled={loading}
              style={{ padding: '10px 24px', background: '#2563EB', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
            >
              {loading ? 'Submitting...' : 'Dispatch Ticket'}
            </button>
          </div>
        </form>
      </section>

      <section>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ margin: 0 }}>Live Incident Feed ({displayedComplaints.length})</h3>
          
          <div style={{ display: 'flex', gap: '8px' }}>
            {['ALL', 'PENDING', 'IN_PROGRESS', 'RESOLVED'].map(status => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                style={{
                  padding: '4px 12px',
                  borderRadius: '16px',
                  border: '1px solid #cbd5e1',
                  background: filterStatus === status ? '#2563EB' : '#fff',
                  color: filterStatus === status ? '#fff' : '#475569',
                  cursor: 'pointer',
                  fontSize: '12px',
                  fontWeight: 'bold'
                }}
              >
                {status}
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {displayedComplaints.map((item) => (
            <div
              key={item.id}
              style={{ border: '1px solid #e2e8f0', padding: '16px', borderRadius: '6px', background: '#ffffff', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <strong style={{ fontSize: '16px' }}>{item.title}</strong>
                <span style={{ padding: '3px 8px', borderRadius: '12px', fontSize: '12px', fontWeight: 'bold', background: item.status === 'RESOLVED' ? '#DCFCE7' : item.status === 'IN_PROGRESS' ? '#DBEAFE' : '#FEF3C7', color: item.status === 'RESOLVED' ? '#166534' : item.status === 'IN_PROGRESS' ? '#1E40AF' : '#92400E' }}>
                  {item.status || 'PENDING'}
                </span>
              </div>
              <p style={{ margin: '0 0 8px 0', color: '#475569' }}>{item.description}</p>
              <small style={{ color: '#94A3B8', display: 'block', marginBottom: '12px' }}>
                Priority: <b>{item.priority || 'NORMAL'}</b> | Dept: <b>{item.department || 'General'}</b> | Ticket #{item.id}
              </small>
              
              {item.status !== 'RESOLVED' && (
                <div style={{ display: 'flex', gap: '8px', borderTop: '1px solid #f1f5f9', paddingTop: '12px' }}>
                  {item.status !== 'IN_PROGRESS' && (
                    <button 
                      onClick={() => handleUpdateStatus(item.id, 'IN_PROGRESS')}
                      style={{ fontSize: '12px', padding: '6px 12px', background: '#f1f5f9', color: '#475569', border: '1px solid #cbd5e1', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
                    >
                      Mark In Progress
                    </button>
                  )}
                  <button 
                    onClick={() => handleUpdateStatus(item.id, 'RESOLVED')}
                    style={{ fontSize: '12px', padding: '6px 12px', background: '#10B981', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
                  >
                    Resolve Ticket
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
