import React, { useEffect, useState } from 'react';
import { Layout } from '../../components/ui/Layout';
import { KPICard } from '../../components/ui/KPICard';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { Card } from '../../components/ui/Card';
import { DataTable } from '../../components/ui/DataTable';
import { LineChartWidget, BarChartWidget } from '../../components/ui/Charts';
import { Wallet, Activity, Building2, MapPin } from 'lucide-react';
import api from '../../lib/api';

const mockSurge = [
  { label: 'Mon', value: 12 },
  { label: 'Tue', value: 18 },
  { label: 'Wed', value: 15 },
  { label: 'Thu', value: 22 },
  { label: 'Fri', value: 25 },
  { label: 'Sat', value: 20 },
  { label: 'Sun', value: 16 },
];

const mockHospitals = [
  { name: 'CityCare Hospital', distance: '1.2 km', beds: 12, icu: 3 },
  { name: 'Metro Health Center', distance: '2.4 km', beds: 5, icu: 1 },
  { name: 'Green Valley Clinic', distance: '3.1 km', beds: 8, icu: 2 },
];

export default function PatientDashboard() {
  const [wallet, setWallet] = useState({ balance: 0, last_txn: null });
  const [referrals, setReferrals] = useState([]);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const [w, r, a] = await Promise.allSettled([
          api.get('/api/wallet/balance'),
          api.get('/api/patients/referrals?limit=5'),
          api.get('/api/patients/alerts?limit=5'),
        ]);
        if (w.status === 'fulfilled') setWallet(w.value.data);
        if (r.status === 'fulfilled') setReferrals(r.value.data?.referrals || []);
        if (a.status === 'fulfilled') setAlerts(a.value.data?.alerts || []);
      } catch {}
    };
    load();
  }, []);

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Patient Dashboard</h1>
          <p className="text-sm text-gray-600">Nearby hospitals, referrals, wallet, and health alerts</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <KPICard title="Wallet Balance" value={`₹${(wallet?.balance ?? 0).toFixed(2)}`} sublabel="Razorpay powered" icon={Wallet} tone="success" />
          <KPICard title="Active Referrals" value={referrals.filter(r => r.status !== 'discharged').length} sublabel="In progress" icon={Activity} tone="info" />
          <KPICard title="Surge Risk" value="Moderate" sublabel="AI prediction" icon={Building2} />
          <KPICard title="Nearest Hospital" value={mockHospitals[0].distance} sublabel={mockHospitals[0].name} icon={MapPin} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="p-5 lg:col-span-2">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold">Nearby Hospitals</h2>
              <a href="/patient/search" className="text-sm text-blue-600">Open Search</a>
            </div>
            <div className="space-y-3">
              {mockHospitals.map((h) => (
                <div key={h.name} className="px-3 py-3 border rounded-xl flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{h.name}</p>
                    <p className="text-xs text-gray-600">{h.distance} · Beds {h.beds} · ICU {h.icu}</p>
                  </div>
                  <button className="text-sm text-blue-600">View</button>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-5">
            <h2 className="text-lg font-semibold mb-3">AI Health Alerts</h2>
            <ul className="space-y-2">
              {alerts.length === 0 ? (
                <li className="text-sm text-gray-600">No alerts</li>
              ) : (
                alerts.map((a) => (
                  <li key={a.id} className="text-sm flex items-center justify-between">
                    <span>{a.title}</span>
                    <StatusBadge status={a.severity || 'pending'} />
                  </li>
                ))
              )}
            </ul>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="p-5">
            <h2 className="text-lg font-semibold mb-3">Surge Prediction (7d)</h2>
            <LineChartWidget data={mockSurge} />
          </Card>
          <Card className="p-5">
            <h2 className="text-lg font-semibold mb-3">Referral Timeline</h2>
            <DataTable
              columns={[
                { key: 'id', header: 'ID' },
                { key: 'hospital', header: 'Hospital' },
                { key: 'created_at', header: 'Date' },
                { key: 'status', header: 'Status', cell: (v) => <StatusBadge status={v} /> },
              ]}
              data={referrals.map((r) => ({
                id: r.id?.slice(-6) || '—',
                hospital: r.hospital_name || r.to_hospital_name || '—',
                created_at: r.created_at ? new Date(r.created_at).toLocaleString() : '—',
                status: r.status || 'pending',
              }))}
              empty="No referrals yet"
            />
          </Card>
        </div>
      </div>
    </Layout>
  );
}
