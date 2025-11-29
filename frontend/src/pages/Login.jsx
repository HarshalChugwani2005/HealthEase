import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Button } from '../components/ui/Button';
import { StatusBadge } from '../components/ui/StatusBadge';
import { ShieldCheck, WifiOff } from 'lucide-react';
import api from '../lib/api';

const Login = () => {
    const navigate = useNavigate();
    const { login, isLoading, error } = useAuthStore();

    const [formData, setFormData] = useState({
        email: '',
        password: '',
        role: 'patient',
    });
    const [serverError, setServerError] = useState(null);

    useEffect(() => {
        // Quick health check to inform user if backend is down
        (async () => {
            try {
                await api.get('/health');
                setServerError(null);
            } catch (err) {
                console.error("Health check failed:", err);
                setServerError(err.message || "Backend unreachable");
            }
        })();
    }, []);



    const handleSubmit = async (e) => {
        e.preventDefault();
        const result = await login(formData.email, formData.password);

        if (result.success) {
            // Redirect based on role
            const roleRedirects = {
                hospital: '/hospital/dashboard',
                patient: '/patient/dashboard',
                admin: '/admin/dashboard',
            };
            navigate(roleRedirects[result.role] || '/');
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
            <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 animate-slide-in-up">
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h1>
                    <p className="text-gray-600">Sign in to HealthEase</p>
                </div>

                {/* Backend Offline Banner */}
                {/* Backend Offline Banner */}
                {serverError && (
                    <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 text-sm flex items-center gap-2">
                        <WifiOff className="h-4 w-4" /> {serverError}. Check server on http://localhost:8000
                    </div>
                )}

                {/* Error Message */}
                {error && (
                    <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                        {error}
                    </div>
                )}

                {/* Login Form */}
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-2">
                            Continue as
                        </label>
                        <select
                            id="role"
                            value={formData.role}
                            onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        >
                            <option value="patient">Patient</option>
                            <option value="hospital">Hospital Admin</option>
                            <option value="admin">Super Admin</option>
                        </select>
                    </div>
                    <div>
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                            Email Address
                        </label>
                        <input
                            id="email"
                            type="email"
                            required
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                            placeholder="you@example.com"
                        />
                    </div>

                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                            Password
                        </label>
                        <input
                            id="password"
                            type="password"
                            required
                            value={formData.password}
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                            placeholder="••••••••"
                        />
                    </div>

                    <Button
                        type="submit"
                        variant="primary"
                        size="lg"
                        className="w-full"
                        isLoading={isLoading}
                    >
                        Sign In
                    </Button>
                </form>

                {/* Footer */}
                <div className="mt-6 text-center">
                    <p className="text-sm text-gray-600">
                        Don't have an account?{' '}
                        <Link to="/register" className="text-blue-600 hover:text-blue-700 font-medium">
                            Sign up
                        </Link>
                    </p>
                    <div className="mt-4 flex items-center justify-center gap-2 text-xs text-gray-600">
                        <ShieldCheck className="h-4 w-4 text-emerald-600" />
                        <span>JWT secured sessions with role-based access</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
