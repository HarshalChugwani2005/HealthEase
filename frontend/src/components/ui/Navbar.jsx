import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { NotificationCenter } from './NotificationCenter';
import { Home, Hospital, User, LogOut, BarChart } from 'lucide-react';

const Navbar = ({ role }) => {
    const { user, logout } = useAuthStore();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    // Different navigation for each role
    const navigation = {
        hospital: [
            { name: 'Dashboard', href: '/hospital/dashboard', icon: Home },
            { name: 'Inventory', href: '/hospital/inventory', icon: BarChart },
            { name: 'Referrals', href: '/hospital/referrals', icon: Hospital },
            { name: 'Wallet', href: '/hospital/wallet', icon: User },
        ],
        patient: [
            { name: 'Find Hospitals', href: '/patient/search', icon: Hospital },
            { name: 'Appointments', href: '/patient/appointments', icon: BarChart },
            { name: 'My Referrals', href: '/patient/referral', icon: BarChart },
            { name: 'Alerts', href: '/patient/alerts', icon: Home },
            { name: 'Profile', href: '/patient/profile', icon: User },
        ],
        admin: [
            { name: 'Hospitals', href: '/admin/hospitals', icon: Hospital },
            { name: 'Analytics', href: '/admin/analytics', icon: BarChart },
        ],
    };

    const navItems = navigation[role] || [];

    // Theme colors based on role
    const themeColors = {
        hospital: 'bg-hospital-primary',
        patient: 'bg-patient-primary',
        admin: 'bg-admin-primary',
    };

    return (
        <nav className={`${themeColors[role] || 'bg-gray-900'} text-white shadow-lg`}>
            <div className="container mx-auto px-4">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <div className="flex items-center">
                        <Link to="/" className="text-2xl font-bold">
                            HealthEase
                        </Link>
                    </div>

                    {/* Navigation Links */}
                    <div className="hidden md:flex items-center space-x-4">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            return (
                                <Link
                                    key={item.name}
                                    to={item.href}
                                    className="flex items-center px-3 py-2 rounded-md text-sm font-medium hover:bg-white/10 transition-colors"
                                >
                                    <Icon className="w-4 h-4 mr-2" />
                                    {item.name}
                                </Link>
                            );
                        })}
                    </div>

                    {/* User Menu */}
                    <div className="flex items-center space-x-4">
                        <NotificationCenter />
                        <span className="text-sm">{user?.email}</span>
                        <button
                            onClick={handleLogout}
                            className="flex items-center px-3 py-2 rounded-md text-sm font-medium hover:bg-white/10 transition-colors"
                        >
                            <LogOut className="w-4 h-4 mr-2" />
                            Logout
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
