import React, { useState } from 'react';
import { loginUser, createComplaint } from './services/api';
import Dashboard from './components/Dashboard';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('access_token'));
  const [email, setEmail] = useState('admin@campus.edu');
  const [password, setPassword] = useState('admin123');

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const data = await loginUser(email, password);
      localStorage.setItem('access_token', data.access_token);
      setToken(data.access_token);
      alert('Login successful!');
    } catch (err) {
      alert('Login failed: Check credentials');
    }
  };

  const handleSubmitComplaint = async (e) => {
    e.preventDefault();
    try {
      await createComplaint({ title, description, location });
      setTitle('');
      setDescription('');
      setLocation('');
    } catch (err) {
      alert('Failed to submit complaint');
    }
  };

  if (!token) {
    return (
      <div style={{ padding: '30px', fontFamily: 'sans-serif' }}>
        <h2>AI Smart Campus - Login</h2>
        <form onSubmit={handleLogin}>
          <div>
            <label>Email: </label>
            <input value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <br />
          <div>
            <label>Password: </label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <br />
          <button type="submit">Log In</button>
        </form>
      </div>
    );
  }

  return (
    <div style={{ padding: '30px', fontFamily: 'sans-serif' }}>
      <h1>AI Smart Campus Platform</h1>
      <button onClick={() => { localStorage.clear(); setToken(null); }}>Log Out</button>
      <hr />
      
      <h3>Submit New Complaint</h3>
      <form onSubmit={handleSubmitComplaint} style={{ marginBottom: '20px' }}>
        <div>
          <input placeholder="Title (e.g. AC leaking)" value={title} onChange={(e) => setTitle(e.target.value)} required />
        </div>
        <br />
        <div>
          <textarea placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} required />
        </div>
        <br />
        <div>
          <input placeholder="Location (e.g. Room 302)" value={location} onChange={(e) => setLocation(e.target.value)} required />
        </div>
        <br />
        <button type="submit">Submit Complaint</button>
      </form>

      <hr />
      <Dashboard />
    </div>
  );
}