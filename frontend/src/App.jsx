import React, { useState } from 'react';
import { loginUser } from './services/api';
import Dashboard from './components/Dashboard';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('access_token'));
  const [email, setEmail] = useState('admin@campus.edu');
  const [password, setPassword] = useState('AdminPass123!');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await loginUser(email, password);
      localStorage.setItem('access_token', data.access_token);
      setToken(data.access_token);
    } catch (err) {
      setError('Login failed: Check your email and password.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setToken(null);
  };

  if (token) {
    return <Dashboard onLogout={handleLogout} />;
  }

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      backgroundColor: '#0f172a',
      fontFamily: 'sans-serif'
    }}>
      <div style={{
        background: '#1e293b',
        padding: '32px',
        borderRadius: '8px',
        width: '360px',
        boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ color: '#ffffff', marginTop: 0, marginBottom: '20px' }}>AI Smart Campus</h2>
        {error && (
          <div style={{
            background: '#ef444420',
            color: '#ef4444',
            padding: '10px',
            borderRadius: '4px',
            marginBottom: '16px',
            fontSize: '14px'
          }}>
            {error}
          </div>
        )}
        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <label style={{ color: '#cbd5e1', fontSize: '14px', display: 'block', marginBottom: '4px' }}>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '4px',
                border: '1px solid #334155',
                background: '#0f172a',
                color: '#fff',
                boxSizing: 'border-box'
              }}
            />
          </div>
          <div>
            <label style={{ color: '#cbd5e1', fontSize: '14px', display: 'block', marginBottom: '4px' }}>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '4px',
                border: '1px solid #334155',
                background: '#0f172a',
                color: '#fff',
                boxSizing: 'border-box'
              }}
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '10px',
              marginTop: '8px',
              backgroundColor: '#2563eb',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              fontWeight: 'bold',
              cursor: 'pointer'
            }}
          >
            {loading ? 'Signing In...' : 'Log In'}
          </button>
        </form>
      </div>
    </div>
  );
}
