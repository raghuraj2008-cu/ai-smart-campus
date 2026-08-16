import axios from 'axios';

const API = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercept requests to attach Bearer token
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const loginUser = async (email, password) => {
  // Sends standard JSON payload matching the backend schema
  const response = await API.post('/auth/login', {
    email,
    password,
  });
  return response.data;
};

export const fetchComplaints = async () => {
  const response = await API.get('/complaints/');
  return response.data;
};

export const createComplaint = async (payload) => {
  const response = await API.post('/complaints/', payload);
  return response.data;
};

export default API;