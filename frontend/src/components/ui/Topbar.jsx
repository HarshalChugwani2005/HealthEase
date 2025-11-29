import React from 'react';
import { useAuthStore } from '../../store/authStore';
import { Bell, Search, LogOut, ShieldCheck, UserCircle } from 'lucide-react';
import { NotificationCenter } from './NotificationCenter';

export const Topbar = ({ onMenu }) => {
  const { user, logout } = useAuthStore();

  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

  return (
    <header className="sticky top-0 z-20 h-16 flex items-center justify-between bg-white border-b px-4 md:px-6">
      <div className="flex items-center gap-3">
        <button onClick={onMenu} className="md:hidden inline-flex items-center justify-center h-9 w-9 border rounded-lg">
          ☰
        </button>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="search"
            placeholder="Search hospitals, referrals, patients..."
            className="pl-9 pr-3 h-10 w-[220px] md:w-[360px] rounded-lg border focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        {token && (
          <span className="hidden sm:inline-flex items-center gap-1 text-xs text-gray-600 border rounded-full px-2 py-1">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" /> JWT Active
          </span>
        )}
        <NotificationCenter icon={<Bell className="h-5 w-5" />} />
        <div className="flex items-center gap-2 text-sm text-gray-700">
          <UserCircle className="h-5 w-5 text-gray-500" />
          <span className="hidden sm:inline">{user?.email}</span>
        </div>
        <button onClick={logout} className="text-sm text-gray-600 hover:text-gray-900">Sign out</button>
      </div>
    </header>
  );
};
