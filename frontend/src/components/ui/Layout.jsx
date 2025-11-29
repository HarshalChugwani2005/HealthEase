import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export const Layout = ({ children }) => {
  const [open, setOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex">
        <div className="hidden md:block">
          <Sidebar />
        </div>
        {/* Mobile drawer */}
        {open && (
          <div className="fixed inset-0 z-30 bg-black/30 md:hidden" onClick={() => setOpen(false)} />
        )}
        <div className={`fixed z-40 inset-y-0 left-0 w-64 transform bg-white border-r md:hidden transition-transform ${open ? 'translate-x-0' : '-translate-x-full'}`}>
          <Sidebar />
        </div>

        <div className="flex-1 min-w-0">
          <Topbar onMenu={() => setOpen((v) => !v)} />
          <main className="p-4 md:p-6 space-y-6">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
};
