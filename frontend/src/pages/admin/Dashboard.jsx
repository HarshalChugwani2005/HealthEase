import React, { useEffect, useState } from 'react';
import { Layout } from '../../components/ui/Layout';
import { KPICard } from '../../components/ui/KPICard';
import { DataTable } from '../../components/ui/DataTable';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { Card } from '../../components/ui/Card';
import { BarChartWidget, LineChartWidget } from '../../components/ui/Charts';
import { Building2, Wallet, TrendingUp, GitBranch } from 'lucide-react';
import api from '../../lib/api';

export default function AdminDashboard() {
  const [hospitals, setHospitals] = useState([]);
  const [ads, setAds] = useState([]);
  const [payouts, setPayouts] = useState([]);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const [h, a, p, l] = await Promise.allSettled([
          api.get('/api/admin/hospitals?limit=5'),
          api.get('/api/admin/advertisements?limit=5'),
          api.get('/api/admin/payouts?limit=5'),
          api.get('/api/admin/n8n-logs?limit=5'),
        ]);
        if (h.status === 'fulfilled') setHospitals(h.value.data?.hospitals || []);
        if (a.status === 'fulfilled') setAds(a.value.data?.ads || []);
        if (p.status === 'fulfilled') setPayouts(p.value.data?.payouts || []);
        if (l.status === 'fulfilled') setLogs(l.value.data?.logs || []);
      } catch {}
    };
    load();
  }, []);

  const kpiData = [
    { title: 'Total Hospitals', value: hospitals.length || 128, icon: Building2 },
    { title: "Today’s Revenue", value: '₹2.4L', icon: Wallet, tone: 'success' },
    { title: 'Active Referrals', value: 56, icon: TrendingUp, tone: 'info' },
    { title: 'Surge Risk (avg)', value: 'Moderate', icon: GitBranch },
  ];

  const mockInflow = [
    { label: '09:00', value: 10 },
    { label: '10:00', value: 18 },
    { label: '11:00', value: 22 },
    { label: '12:00', value: 19 },
    { label: '13:00', value: 25 },
  ];

  const mockSurge = [
    { label: 'Mon', value: 12 },
    { label: 'Tue', value: 18 },
    { label: 'Wed', value: 15 },
    { label: 'Thu', value: 22 },
    { label: 'Fri', value: 25 },
    { label: 'Sat', value: 20 },
    { label: 'Sun', value: 16 },
  ];

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">System Overview</h1>
          <p className="text-sm text-gray-600">Global operations, analytics, advertisements, payouts, and workflows</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {kpiData.map((k) => (
            <KPICard key={k.title} title={k.title} value={k.value} icon={k.icon} tone={k.tone || 'default'} />
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="p-5 lg:col-span-2">
            <h2 className="text-lg font-semibold mb-3">Patient Inflow (Today)</h2>
            <BarChartWidget data={mockInflow} />
          </Card>
          <Card className="p-5">
            <h2 className="text-lg font-semibold mb-3">Surge Predictions (7d)</h2>
            <LineChartWidget data={mockSurge} />
          </Card>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <Card className="p-5">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Hospitals</h2>
              <a href="/admin/hospitals" className="text-sm text-blue-600">Manage</a>
            </div>
            <DataTable
              columns={[
                { key: 'name', header: 'Name' },
                { key: 'city', header: 'City' },
                { key: 'occupancy', header: 'Occupancy' },
                { key: 'status', header: 'Status', cell: (v) => <StatusBadge status={v || 'pending'} /> },
              ]}
              data={hospitals.map((h) => ({
                name: h.name || '—',
                city: h.city || '—',
                occupancy: `${h.occupied_beds ?? '—'} / ${h.total_beds ?? '—'}`,
                status: h.status || 'active',
              }))}
            />
          </Card>

          <Card className="p-5">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">n8n Workflow Logs</h2>
              <a href="/admin/workflows" className="text-sm text-blue-600">View all</a>
            </div>
            <DataTable
              columns={[
                { key: 'id', header: 'ID' },
                { key: 'name', header: 'Workflow' },
                { key: 'status', header: 'Status', cell: (v) => <StatusBadge status={v || 'pending'} /> },
                { key: 'created_at', header: 'When' },
              ]}
              data={logs.map((l) => ({
                id: l.id?.slice(-6) || '—',
                name: l.name || l.workflow_name || '—',
                status: l.status || 'completed',
                created_at: l.created_at ? new Date(l.created_at).toLocaleString() : '—',
              }))}
            />
          </Card>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <Card className="p-5">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Advertisements</h2>
              <a href="/admin/ads" className="text-sm text-blue-600">Manage</a>
            </div>
            <DataTable
              columns={[
                { key: 'title', header: 'Title' },
                { key: 'hospital', header: 'Hospital' },
                { key: 'status', header: 'Status', cell: (v) => <StatusBadge status={v || 'pending'} /> },
              ]}
              data={ads.map((a) => ({
                title: a.title || '—',
                hospital: a.hospital_name || '—',
                status: a.status || 'active',
              }))}
              empty="No ads"
            />
          </Card>

          <Card className="p-5">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Payouts</h2>
              <a href="/admin/payouts" className="text-sm text-blue-600">Review</a>
            </div>
            <DataTable
              columns={[
                { key: 'id', header: 'ID' },
                { key: 'hospital', header: 'Hospital' },
                { key: 'amount', header: 'Amount' },
                { key: 'status', header: 'Status', cell: (v) => <StatusBadge status={v || 'pending'} /> },
              ]}
              data={payouts.map((p) => ({
                id: p.id?.slice(-6) || '—',
                hospital: p.hospital_name || '—',
                amount: `₹${(p.amount || 0).toFixed(2)}`,
                status: p.status || 'pending',
              }))}
              empty="No payouts"
            />
          </Card>
        </div>
      </div>
    </Layout>
  );
}
