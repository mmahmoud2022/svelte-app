import { writable } from 'svelte/store';
import type { User } from '../api';
import { getCurrentUser, logout as apiLogout } from '../api';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const createAuthStore = () => {
  const { subscribe, set, update } = writable<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });

  return {
    subscribe,
    
    // Initialize auth state on app load
    init: async () => {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        set({ user: null, isAuthenticated: false, isLoading: false });
        return;
      }

      try {
        const user = await getCurrentUser();
        set({ user, isAuthenticated: true, isLoading: false });
      } catch (error) {
        // Token is invalid, clear it
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ user: null, isAuthenticated: false, isLoading: false });
      }
    },

    // Login - store tokens and user
    login: (accessToken: string, refreshToken: string, user: User) => {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
      set({ user, isAuthenticated: true, isLoading: false });
    },

    // Logout
    logout: async () => {
      try {
        await apiLogout();
      } catch (error) {
        console.error('Logout error:', error);
      }
      
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      set({ user: null, isAuthenticated: false, isLoading: false });
    },

    // Update user info
    updateUser: (user: User) => {
      update(state => ({ ...state, user }));
    },

    // Clear auth state
    clear: () => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      set({ user: null, isAuthenticated: false, isLoading: false });
    },
  };
};

export const authStore = createAuthStore();

// Helper to check if user has a specific role (case-insensitive)
export const hasRole = (user: User | null, role: 'PATIENT' | 'DOCTOR' | 'ADMIN' | 'patient' | 'doctor' | 'admin'): boolean => {
  if (!user?.role) return false;
  return user.role.toUpperCase() === role.toUpperCase();
};

// Helper to check if user is admin
export const isAdmin = (user: User | null): boolean => {
  return hasRole(user, 'ADMIN');
};

// Helper to check if user is doctor
export const isDoctor = (user: User | null): boolean => {
  return hasRole(user, 'DOCTOR');
};

// Helper to check if user is patient
export const isPatient = (user: User | null): boolean => {
  return hasRole(user, 'PATIENT');
};
