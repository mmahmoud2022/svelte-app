import axios from 'axios';
import type { AxiosError, AxiosResponse } from 'axios';

// API Base URL - adjust based on environment
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;

    // Don't try to refresh token on login/register endpoints
    const isAuthEndpoint = originalRequest.url?.includes('/auth/login') || 
                          originalRequest.url?.includes('/auth/register');

    // If token expired and we have a refresh token
    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, clear tokens and redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      } else {
        // No refresh token, redirect to login
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// =============== Type Definitions ===============

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'patient' | 'doctor' | 'admin' | 'PATIENT' | 'DOCTOR' | 'ADMIN'; // Support both cases
  is_active: boolean;
  email_verified: boolean;
  admin_approved?: boolean;
  created_at: string;
}

export interface RegistrationResponse {
  success: boolean;
  message: string;
  user: User;
  next_steps: string[];
  requires_verification: boolean;
  requires_admin_approval: boolean;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface AdminActionResponse {
  success: boolean;
  message: string;
  action: string;
  user_id: number;
  user_email: string;
  user_name: string;
  user_role: string;
  performed_by: string;
  performed_at: string;
  details: Record<string, any>;
}

export interface StatisticsResponse {
  total_users: number;
  total_doctors: number;
  total_patients: number;
  pending_doctors: number;
  active_users: number;
}

export interface PatientRegistrationData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
  gender?: string;
  date_of_birth?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relationship?: string;
  marketing_consent?: boolean;
}

export interface DoctorRegistrationData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
  gender?: string;
  specialization: string;
  consultation_fee?: number;
  bio?: string;
  languages_spoken?: string;
}

export interface AdminRegistrationData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
  admin_secret: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

// =============== API Functions ===============

// Statistics (Public)
export const getStatistics = async (): Promise<StatisticsResponse> => {
  const response = await api.get<StatisticsResponse>('/api/v1/auth/statistics');
  return response.data;
};

// Authentication
export const registerPatient = async (
  data: PatientRegistrationData
): Promise<RegistrationResponse> => {
  const response = await api.post<RegistrationResponse>('/api/v1/auth/register/patient', data);
  return response.data;
};

export const registerDoctor = async (
  data: DoctorRegistrationData
): Promise<RegistrationResponse> => {
  const response = await api.post<RegistrationResponse>('/api/v1/auth/register/doctor', data);
  return response.data;
};

export const registerAdmin = async (
  data: AdminRegistrationData
): Promise<RegistrationResponse> => {
  const response = await api.post<RegistrationResponse>('/api/v1/auth/register/admin', data);
  return response.data;
};

export const login = async (credentials: LoginCredentials): Promise<LoginResponse> => {
  const response = await api.post<LoginResponse>('/api/v1/auth/login', {
    email: credentials.email,
    password: credentials.password,
  });
  return response.data;
};

export const logout = async (): Promise<void> => {
  const refreshToken = localStorage.getItem('refresh_token');
  if (refreshToken) {
    await api.post('/api/v1/auth/logout', { refresh_token: refreshToken });
  }
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get<User>('/api/v1/auth/me');
  return response.data;
};

// Admin endpoints
export const getAllUsers = async (): Promise<User[]> => {
  const response = await api.get<User[]>('/api/v1/admin/users');
  return response.data;
};

export const getPendingDoctors = async (): Promise<User[]> => {
  const response = await api.get<User[]>('/api/v1/admin/doctors/pending');
  return response.data;
};

export const approveDoctor = async (doctorId: number): Promise<AdminActionResponse> => {
  const response = await api.post<AdminActionResponse>(`/api/v1/admin/doctors/${doctorId}/approve`);
  return response.data;
};

export const rejectDoctor = async (doctorId: number, reason: string): Promise<AdminActionResponse> => {
  const response = await api.post<AdminActionResponse>(`/api/v1/admin/doctors/${doctorId}/reject`, {
    reason,
  });
  return response.data;
};

export const suspendUser = async (
  userId: number,
  reason: string
): Promise<AdminActionResponse> => {
  const response = await api.post<AdminActionResponse>(`/api/v1/admin/users/${userId}/suspend`, {
    reason,
  });
  return response.data;
};

export const activateUser = async (userId: number): Promise<AdminActionResponse> => {
  const response = await api.post<AdminActionResponse>(`/api/v1/admin/users/${userId}/activate`);
  return response.data;
};

export const deleteUser = async (userId: number): Promise<AdminActionResponse> => {
  const response = await api.delete<AdminActionResponse>(`/api/v1/admin/users/${userId}`);
  return response.data;
};

export default api;
