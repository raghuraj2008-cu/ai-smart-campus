import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function AnalyticsCard() {
  const [data, setData] = useState(null);
  const [days, setDays] = useState('30');

  const fetchStats = async (selectedDays) => {
    try {
      const token = localStorage.getItem('access_token');
      let url = 'http://localhost:8000/api/v1/analytics/summary';
      
      if (selectedDays !== 'all') {
        const start = new Date();
        start.setDate(start.getDate() - parseInt(selectedDays));
        url += `?start_date=${start.toISOString()}`;
      }

      const res = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setData(res.data);
    } catch (err) {
      console.error('Failed to load metrics', err);
    }
  };

  const handleExportCSV = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/api/v1/complaints/export/csv', {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob',
      });
      
      const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = blobUrl;
      link.setAttribute('download', `complaints_report.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to download CSV');
    }
  };

  useEffect(() => {
    fetchStats(days);
  }, [days]);

  if (!data) return <div>Loading Analytics...</div>;

  return (
    <div style={{ border: '1px solid #ddd', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3>📊 Campus Overview</h3>
        <div>
          <select value={days} onChange={(e) => setDays(e.target.value)} style={{ marginRight: '10px' }}>
            <option value="7">Last 7 Days</option>
            <option value="30">Last 30 Days</option>
            <option value="all">All Time</option>
          </select>
          <button onClick={handleExportCSV}>📥 Export CSV</button>
        </div>
      </div>
      
      <p><strong>Total Tickets:</strong> {data.total_complaints}</p>
      
      <div style={{ display: 'flex', gap: '30px' }}>
        <div>
          <h4>By Status</h4>
          {Object.entries(data.by_status).map(([k, v]) => (
            <div key={k}>{k}: <strong>{v}</strong></div>
          ))}
        </div>
        <div>
          <h4>By Department</h4>
          {Object.entries(data.by_department).map(([k, v]) => (
            <div key={k}>{k}: <strong>{v}</strong></div>
          ))}
        </div>
        <div>
          <h4>By Priority</h4>
          {Object.entries(data.by_priority).map(([k, v]) => (
            <div key={k}>{k}: <strong>{v}</strong></div>
          ))}
        </div>
      </div>
    </div>
  );
}