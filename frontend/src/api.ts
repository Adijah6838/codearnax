import axios from 'axios';

export const api = axios.create({
  baseURL: 'http://127.0.0.1:8010',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Automatically attach the token to every request if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});