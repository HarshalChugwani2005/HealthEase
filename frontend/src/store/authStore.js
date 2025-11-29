import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../lib/api';

export const useAuthStore = create(
    persist(
        (set, get) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,

            // Login action
            login: async (email, password) => {
                set({ isLoading: true, error: null });
                try {
                    const response = await api.post('/api/auth/login', { email, password });
                    const { user, access_token } = response.data;

                    localStorage.setItem('access_token', access_token);

                    set({
                        user,
                        token: access_token,
                        isAuthenticated: true,
                        isLoading: false,
                    });

                    return { success: true, role: user.role };
                } catch (error) {
                    let errorMessage = 'Login failed';
                    // Network/timeout
                    if (error.code === 'NETWORK_ERROR') {
                        errorMessage = `Cannot reach backend at ${import.meta.env.VITE_API_URL || 'http://localhost:8000'}`;
                    } else if (error.response) {
                        const status = error.response.status;
                        const detail = error.response.data?.detail;
                        if (status === 401) {
                            errorMessage = 'Invalid email or password';
                        } else if (status === 403) {
                            errorMessage = 'Account is inactive or forbidden';
                        } else if (status === 503) {
                            errorMessage = 'Service temporarily unavailable (database)';
                        } else if (status === 422) {
                            errorMessage = 'Invalid input. Please verify your email/password.';
                        } else if (typeof detail === 'string') {
                            errorMessage = detail;
                        } else if (detail) {
                            errorMessage = JSON.stringify(detail);
                        }
                    }
                    set({ error: errorMessage, isLoading: false });
                    return { success: false, error: errorMessage };
                }
            },

            // Register action
            register: async (email, password, role, profile_data) => {
                set({ isLoading: true, error: null });
                try {
                    const response = await api.post('/api/auth/register', {
                        email,
                        password,
                        role,
                        profile_data,
                    });
                    const { user, access_token } = response.data;

                    localStorage.setItem('access_token', access_token);

                    set({
                        user,
                        token: access_token,
                        isAuthenticated: true,
                        isLoading: false,
                    });

                    return { success: true, role: user.role };
                } catch (error) {
                    let errorMessage = 'Registration failed';
                    if (error.code === 'NETWORK_ERROR') {
                        errorMessage = `Cannot reach backend at ${import.meta.env.VITE_API_URL || 'http://localhost:8000'}`;
                    } else if (error.response) {
                        const status = error.response.status;
                        const detail = error.response.data?.detail;
                        if (status === 503) {
                            errorMessage = 'Service temporarily unavailable (database)';
                        } else if (typeof detail === 'string') {
                            errorMessage = detail;
                        } else if (detail) {
                            errorMessage = JSON.stringify(detail);
                        }
                    }
                    set({ error: errorMessage, isLoading: false });
                    return { success: false, error: errorMessage };
                }
            },

            // Logout action
            logout: () => {
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
                set({
                    user: null,
                    token: null,
                    isAuthenticated: false,
                    error: null,
                });
            },

            // Fetch current user
            fetchUser: async () => {
                const token = localStorage.getItem('access_token');
                if (!token) {
                    set({ isAuthenticated: false });
                    return;
                }

                try {
                    const response = await api.get('/api/auth/me');
                    set({
                        user: response.data,
                        token,
                        isAuthenticated: true,
                    });
                } catch (error) {
                    get().logout();
                }
            },
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({
                user: state.user,
                token: state.token,
                isAuthenticated: state.isAuthenticated,
            }),
        }
    )
);
