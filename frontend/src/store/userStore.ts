/**
 * User Store - Zustand
 * Manages user authentication state
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI } from '@/lib/api';

interface User {
  id: string;
  email: string;
  name: string;
  plan: string;
  credits: number;
  avatar_url?: string;
}

interface UserState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
  updateCredits: (credits: number) => void;
  fetchCurrentUser: () => Promise<void>;
}

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      
      login: async (email: string, password: string) => {
        set({ isLoading: true });
        try {
          const data = await authAPI.login(email, password);
          const token = data.access_token;
          
          // Store token
          localStorage.setItem('access_token', token);
          
          // Fetch user data
          const userData = await authAPI.getCurrentUser();
          
          set({
            token,
            user: userData,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },
      
      register: async (email: string, password: string, name: string) => {
        set({ isLoading: true });
        try {
          const data = await authAPI.register(email, password, name);
          const token = data.access_token;
          
          // Store token
          localStorage.setItem('access_token', token);
          
          set({
            token,
            user: data.user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },
      
      logout: () => {
        authAPI.logout();
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },
      
      setUser: (user: User) => {
        set({ user });
      },
      
      updateCredits: (credits: number) => {
        const { user } = get();
        if (user) {
          set({ user: { ...user, credits } });
        }
      },
      
      fetchCurrentUser: async () => {
        try {
          const userData = await authAPI.getCurrentUser();
          set({ user: userData, isAuthenticated: true });
        } catch (error) {
          console.error('Failed to fetch user:', error);
        }
      },
    }),
    {
      name: 'user-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
