import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { ChatBot } from './components/ui/ChatBot';

// Pages
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Register from './pages/Register';

// Hospital Pages
import HospitalDashboard from './pages/hospital/Dashboard';
import Inventory from './pages/hospital/Inventory';
import Capacity from './pages/hospital/Capacity';
import Referrals from './pages/hospital/Referrals';
import Wallet from './pages/hospital/Wallet';

// Patient Pages
import PatientDashboard from './pages/patient/Dashboard';
import HospitalSearch from './pages/patient/Search';
import ReferralFlow from './pages/patient/Referral';
import PatientAlerts from './pages/patient/Alerts';
import PatientProfile from './pages/patient/Profile';
import PatientAppointments from './pages/patient/Appointments';

// Admin Pages
import AdminHospitals from './pages/admin/Hospitals';
import AdminAnalytics from './pages/admin/Analytics';
import AdminDashboard from './pages/admin/Dashboard';

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles }) => {
    const { isAuthenticated, user } = useAuthStore();

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (allowedRoles && !allowedRoles.includes(user?.role)) {
        return <Navigate to="/" replace />;
    }

    return children;
};

function App() {
    const { fetchUser, isAuthenticated, user } = useAuthStore();

    useEffect(() => {
        // Fetch user on app load if token exists
        if (localStorage.getItem('access_token')) {
            fetchUser();
        }
    }, [fetchUser]);

    return (
        <BrowserRouter>
            {isAuthenticated && user?.role === 'patient' && <ChatBot />}
            <Routes>
                {/* Public Routes */}
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                {/* Hospital Routes */}
                <Route
                    path="/hospital/dashboard"
                    element={
                        <ProtectedRoute allowedRoles={['hospital']}>
                            <HospitalDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/hospital/inventory"
                    element={
                        <ProtectedRoute allowedRoles={['hospital']}>
                            <Inventory />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/hospital/capacity"
                    element={
                        <ProtectedRoute allowedRoles={['hospital']}>
                            <Capacity />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/hospital/referrals"
                    element={
                        <ProtectedRoute allowedRoles={['hospital']}>
                            <Referrals />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/hospital/wallet"
                    element={
                        <ProtectedRoute allowedRoles={['hospital']}>
                            <Wallet />
                        </ProtectedRoute>
                    }
                />

                {/* Patient Routes */}
                <Route
                    path="/patient/dashboard"
                    element={
                        <ProtectedRoute allowedRoles={['patient']}>
                            <PatientDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/patient/search"
                    element={
                        <ProtectedRoute allowedRoles={['patient']}>
                            <HospitalSearch />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/patient/referral"
                    element={
                        <ProtectedRoute allowedRoles={['patient']}>
                            <ReferralFlow />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/patient/alerts"
                    element={
                        <ProtectedRoute allowedRoles={['patient']}>
                            <PatientAlerts />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/patient/profile"
                    element={
                        <ProtectedRoute allowedRoles={['patient']}>
                            <PatientProfile />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/patient/appointments"
                    element={
                        <ProtectedRoute allowedRoles={['patient']}>
                            <PatientAppointments />
                        </ProtectedRoute>
                    }
                />

                {/* Admin Routes */}
                <Route
                    path="/admin/dashboard"
                    element={
                        <ProtectedRoute allowedRoles={['admin']}>
                            <AdminDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/hospitals"
                    element={
                        <ProtectedRoute allowedRoles={['admin']}>
                            <AdminHospitals />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/analytics"
                    element={
                        <ProtectedRoute allowedRoles={['admin']}>
                            <AdminAnalytics />
                        </ProtectedRoute>
                    }
                />

                {/* 404 */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
