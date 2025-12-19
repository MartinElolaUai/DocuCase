import axios from 'axios';
import { useAuthStore } from '@/store/authStore';

const API_URL = '/api';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  register: (data: {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
  }) => api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
  changePassword: (currentPassword: string, newPassword: string) =>
    api.post('/auth/change-password', { currentPassword, newPassword }),
};

// Users API
export const usersApi = {
  getAll: (params?: Record<string, string>) =>
    api.get('/users', { params }),
  getById: (id: string) => api.get(`/users/${id}`),
  create: (data: Record<string, unknown>) => api.post('/users', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/users/${id}`, data),
  delete: (id: string) => api.delete(`/users/${id}`),
  getSubscriptions: () => api.get('/users/subscriptions'),
  subscribe: (groupId: string) => api.post(`/users/subscriptions/${groupId}`),
  unsubscribe: (groupId: string) =>
    api.delete(`/users/subscriptions/${groupId}`),
};

// Groups API
export const groupsApi = {
  getAll: (params?: Record<string, string>) =>
    api.get('/groups', { params }),
  getById: (id: string) => api.get(`/groups/${id}`),
  create: (data: { name: string; description?: string }) =>
    api.post('/groups', data),
  update: (id: string, data: { name?: string; description?: string }) =>
    api.put(`/groups/${id}`, data),
  delete: (id: string) => api.delete(`/groups/${id}`),
  getSubscribers: (id: string) => api.get(`/groups/${id}/subscribers`),
};

// Applications API
export const applicationsApi = {
  getAll: (params?: Record<string, string>) =>
    api.get('/applications', { params }),
  getById: (id: string) => api.get(`/applications/${id}`),
  create: (data: Record<string, unknown>) => api.post('/applications', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/applications/${id}`, data),
  delete: (id: string) => api.delete(`/applications/${id}`),
  getFeatures: (id: string, params?: Record<string, string>) =>
    api.get(`/applications/${id}/features`, { params }),
  getStats: (id: string) => api.get(`/applications/${id}/stats`),
};

// Features API
export const featuresApi = {
  getAll: (params?: Record<string, string>) =>
    api.get('/features', { params }),
  getById: (id: string) => api.get(`/features/${id}`),
  create: (data: Record<string, unknown>) => api.post('/features', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/features/${id}`, data),
  delete: (id: string) => api.delete(`/features/${id}`),
  getTestCases: (id: string, params?: Record<string, string>) =>
    api.get(`/features/${id}/test-cases`, { params }),
};

// Test Cases API
export const testCasesApi = {
  getAll: (params?: Record<string, string>) =>
    api.get('/test-cases', { params }),
  getById: (id: string) => api.get(`/test-cases/${id}`),
  create: (data: Record<string, unknown>) => api.post('/test-cases', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/test-cases/${id}`, data),
  delete: (id: string) => api.delete(`/test-cases/${id}`),
  getSteps: (id: string) => api.get(`/test-cases/${id}/steps`),
  updateSteps: (id: string, steps: Record<string, unknown>[]) =>
    api.put(`/test-cases/${id}/steps`, { steps }),
  getResults: (id: string, limit?: number) =>
    api.get(`/test-cases/${id}/results`, { params: { limit } }),
};

// Test Requests API
export const testRequestsApi = {
  getAll: (params?: Record<string, string>) =>
    api.get('/test-requests', { params }),
  getById: (id: string) => api.get(`/test-requests/${id}`),
  create: (data: Record<string, unknown>) => api.post('/test-requests', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/test-requests/${id}`, data),
  updateStatus: (
    id: string,
    data: { status: string; assigneeId?: string; notes?: string }
  ) => api.patch(`/test-requests/${id}/status`, data),
  delete: (id: string) => api.delete(`/test-requests/${id}`),
  getMyRequests: (params?: Record<string, string>) =>
    api.get('/test-requests/my-requests', { params }),
};

// Uploads API
export const uploadsApi = {
  uploadTestRequestImage: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    return api.post('/uploads/test-request-images', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

// Pipelines API
export const pipelinesApi = {
  getAll: (params?: Record<string, string>) =>
    api.get('/pipelines', { params }),
  getById: (id: string) => api.get(`/pipelines/${id}`),
  getResults: (id: string) => api.get(`/pipelines/${id}/results`),
  sync: (projectId: string) => api.post('/pipelines/sync', { projectId }),
  registerResult: (data: Record<string, unknown>) =>
    api.post('/pipelines/results', data),
};

// Dashboard API
export const dashboardApi = {
  getStats: () => api.get('/dashboard/stats'),
  getRecentActivity: (limit?: number) =>
    api.get('/dashboard/activity', { params: { limit } }),
  getTestCasesByStatus: (params?: Record<string, string>) =>
    api.get('/dashboard/test-cases-by-status', { params }),
  getPipelineStats: (days?: number) =>
    api.get('/dashboard/pipeline-stats', { params: { days } }),
};

