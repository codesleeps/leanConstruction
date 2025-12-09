import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://localhost:8000'; // Change for production

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle responses
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      AsyncStorage.removeItem('token');
    }
    return Promise.reject(error.response?.data || error.message);
  }
);

export const login = async (email, password) => {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);
  
  return api.post('/token', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getDashboardData = async () => {
  // Mock data for now - replace with actual API call
  return {
    activeProjects: 5,
    completionRate: 67,
    wasteIncidents: 12,
    wasteCost: 2500,
    weeklyTrend: [20, 45, 28, 80, 99, 43, 50],
    alerts: [
      { message: 'High waste detected in Project A', time: '2 hours ago' },
      { message: 'Task completion rate below target', time: '5 hours ago' },
    ],
  };
};

export const getProjects = async () => {
  return api.get('/projects/');
};

export const getProjectDetail = async (projectId) => {
  return api.get(`/projects/${projectId}/`);
};

export const createWasteLog = async (projectId, wasteData) => {
  return api.post(`/projects/${projectId}/waste/`, wasteData);
};

export const uploadImage = async (projectId, imageUri) => {
  const formData = new FormData();
  formData.append('file', {
    uri: imageUri,
    type: 'image/jpeg',
    name: 'photo.jpg',
  });
  
  return api.post(`/projects/${projectId}/upload/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export default api;
