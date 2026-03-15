import axios from 'axios'

// src/api/axios.ts
const api = axios.create({
  baseURL: 'http://localhost:8000', 
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default api