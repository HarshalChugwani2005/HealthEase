import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Home, Building2, User, BarChart2, Wallet, ClipboardList, Layers, GitBranch, Bell, Settings } from 'lucide-react';
import clsx from 'clsx';

const navByRole = {
  patient: [
    { to: '/patient/dashboard', label: 'Dashboard', icon: Home },
    { to: '/patient/search', label: 'Find Hospitals', icon: Building2 },
    { to: '/patient/referral', label: 'Referrals', icon: ClipboardList },
    { to: '/patient/appointments', label: 'Appointments', icon: Layers },
    { to: '/patient/alerts', label: 'Alerts', icon: Bell },
    { to: '/patient/profile', label: 'Profile', icon: User },
  ],
  hospital: [
    { to: '/hospital/dashboard', label: 'Dashboard', icon: Home },
    { to: '/hospital/capacity', label: 'Capacity', icon: BarChart2 },
    { to: '/hospital/inventory', label: 'Inventory', icon: Layers },
    { to: '/hospital/referrals', label: 'Referrals', icon: ClipboardList },
    { to: '/hospital/wallet', label: 'Wallet', icon: Wallet },
    { to: '/hospital/ads', label: 'Advertisements', icon: BarChart2 },
  ],
  admin: [
    { to: '/admin/dashboard', label: 'Overview', icon: Home },
    { to: '/admin/hospitals', label: 'Hospitals', icon: Building2 },
    { to: '/admin/analytics', label: 'Analytics', icon: BarChart2 },
    { to: '/admin/ads', label: 'Advertisements', icon: BarChart2 },
    { to: '/admin/payouts', label: 'Payouts', icon: Wallet },
    { to: '/admin/workflows', label: 'n8n Workflows', icon: GitBranch },
    { to: '/admin/settings', label: 'Settings', icon: Settings },
  ],
};

export const Sidebar = () => {
  const { user } = useAuthStore();
  const loc = useLocation();
  const role = user?.role || 'patient';
  const items = navByRole[role] || [];

  return (
    <aside className="hidden md:flex md:w-64 h-screen sticky top-0 flex-col border-r bg-white">
      <div className="h-16 flex items-center px-4 border-b">
        <div className="text-lg font-bold">
          <span className="text-hospital-primary">Health</span>
          <span className="text-emerald-600">Ease</span>
        </div>
      </div>
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-1 px-2">
          {items.map((item) => {
            const Icon = item.icon;
            const active = loc.pathname === item.to;
            return (
              <li key={item.to}>
                <Link
                  to={item.to}
                  className={clsx(
                    'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium',
                    active ? 'bg-blue-50 text-blue-700 border border-blue-100' : 'text-gray-700 hover:bg-gray-50'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      <div className="p-3 border-t text-xs text-gray-500">AI-powered Hospital Platform</div>
    </aside>
  );
};
