import React, { useEffect, useState } from 'react';
import { fetchComplaints } from '../services/api';
import { useWebSockets } from '../hooks/useWebSockets';
import axios from 'axios';

export default function Dashboard() {
  const [complaints, setComplaints] = useState([]);

  useEffect(() => {
    fetchComplaints().then((data) => setComplaints(data));
  }, []);

  const { isConnected } = useWebSockets((event) => {
    if (event.event === 'COMPLAINT_CREATED') {
      setComplaints((prev) => [event.data, ...prev]);
    } else if (event.event === 'COMPLAINT_STATUS_UPDATED') {
      setComplaints((prev) =>
        prev.map((item) => (item.id === event.data.id ? { ...item, status: event.data.status } : item))
      );
    }
  });

  const handleStatusUpdate = async (id, newStatus) => {
    const token = localStorage.getItem('access_token');
    await axios.patch(
      `http://localhost:8000/api/v1/complaints/${id}/status`,
      { status: newStatus },
      { headers: { Authorization: `Bearer ${token}` } }
    );
  };

  return (
    <div>
      <h2>Campus Complaints Dashboard ({isConnected ? '🟢 Live' : '🔴 Offline'})</h2>
      <ul>
        {complaints.map((item) => (
          <li key={item.id} style={{ marginBottom: '10px' }}>
            <strong>[{item.priority}] {item.title}</strong> — <em>{item.status}</em> ({item.department})
            <div style={{ marginTop: '5px' }}>
              <button onClick={() => handleStatusUpdate(item.id, 'IN_PROGRESS')}>In Progress</button>{' '}
              <button onClick={() => handleStatusUpdate(item.id, 'RESOLVED')}>Resolve</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}