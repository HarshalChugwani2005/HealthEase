import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Layout } from '../../components/ui/Layout';
import { KPICard } from '../../components/ui/KPICard';
import { LineChartWidget, BarChartWidget } from '../../components/ui/Charts';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { Activity, BedSingle, Stethoscope, Wallet as WalletIcon } from 'lucide-react';
import api from '../../lib/api';

const Dashboard = () => {
    const [capacity, setCapacity] = useState(null);
    const [wallet, setWallet] = useState(null);
    const [referrals, setReferrals] = useState([]);
    const [surgePrediction, setSurgePrediction] = useState(null);
    const [forecast, setForecast] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDashboardData();
        // Real-time polling every 30 seconds
        const interval = setInterval(fetchDashboardData, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchDashboardData = async () => {
        try {
            const [capacityRes, walletRes, referralsRes] = await Promise.all([
                api.get('/api/capacity/current'),
                api.get('/api/wallet/balance'),
                api.get('/api/referrals/hospital-referrals', { params: { limit: 5 } })
            ]);

            setCapacity(capacityRes.data);
            setWallet(walletRes.data);
            setReferrals(referralsRes.data.referrals || []);

            try {
                const surgeRes = await api.post('/api/surge/predict', {
                    event_type: 'festival',
                    city: 'Delhi'
                });
                setSurgePrediction(surgeRes.data);
            } catch (err) {
                console.log('Surge prediction unavailable');
            }

            try {
                const forecastRes = await api.get('/api/hospitals/me/health-forecast');
                setForecast(forecastRes.data);
            } catch (err) {
                console.log('Forecast unavailable');
            }
        } catch (err) {
            console.error('Dashboard error:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <Layout>
                <div className="space-y-6">
                    <h1 className="text-2xl font-bold text-gray-900">Hospital Dashboard</h1>
                    <Card className="p-6"><p className="text-gray-600">Loading...</p></Card>
                </div>
            </Layout>
        );
    }

    const occupancyPercentage = capacity ?
        ((capacity.total_beds - capacity.available_beds) / capacity.total_beds * 100).toFixed(1) : 0;

    return (
        <Layout>
            <div className="space-y-6">
                <div className="flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-gray-900">Hospital Dashboard</h1>
                    <Button onClick={fetchDashboardData} variant="outline">Refresh</Button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <KPICard title="Available Beds" value={capacity?.available_beds || 0} sublabel={`of ${capacity?.total_beds || 0} total`} icon={BedSingle} tone="info" />
                    <KPICard title="Occupancy Rate" value={`${occupancyPercentage}%`} sublabel={`${capacity?.total_beds - capacity?.available_beds || 0} occupied`} icon={Activity} tone="warn" />
                    <KPICard title="ICU / Ventilators" value={`${capacity?.icu_beds || 0} / ${capacity?.ventilators || 0}`} sublabel="Available" icon={Stethoscope} />
                    <KPICard title="Wallet Balance" value={`₹${wallet?.balance?.toFixed(2) || '0.00'}`} sublabel={<a href="/hospital/wallet" className="text-blue-600">View details</a>} icon={WalletIcon} tone="success" />
                </div>

                {surgePrediction && (
                    <Card className="p-6 bg-gradient-to-r from-yellow-50 to-orange-50 border-l-4 border-orange-500">
                        <h2 className="text-lg font-semibold text-gray-900 mb-3">🤖 Agentic Command Center</h2>
                        <div className="grid md:grid-cols-2 gap-4">
                            <div>
                                <p className="text-sm text-gray-700 mb-2">
                                    {surgePrediction.predictions?.reasoning}
                                </p>
                                <div className="flex items-center gap-4 mt-3">
                                    <div>
                                        <p className="text-xs text-gray-600">Expected Load</p>
                                        <p className="text-2xl font-bold text-orange-600">
                                            {surgePrediction.predictions?.expected_load || 'N/A'}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-gray-600">Risk Level</p>
                                        <span className={`px-3 py-1 text-xs font-semibold rounded-full ${surgePrediction.predictions?.risk_level === 'high' ? 'bg-red-100 text-red-800' :
                                            surgePrediction.predictions?.risk_level === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-green-100 text-green-800'
                                            }`}>
                                            {surgePrediction.predictions?.risk_level?.toUpperCase() || 'LOW'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div>
                                <p className="text-xs text-gray-600 mb-2">Proactive Actions:</p>
                                <ul className="space-y-2">
                                    {surgePrediction.predictions?.recommendations?.slice(0, 3).map((rec, idx) => (
                                        <li key={idx} className="flex items-center justify-between text-xs text-gray-700 bg-white p-2 rounded border border-orange-100">
                                            <span>{rec}</span>
                                            <button
                                                onClick={async () => {
                                                    try {
                                                        const res = await api.post('/api/hospitals/execute-action', { type: rec });
                                                        alert(res.data.message);
                                                        fetchDashboardData(); // Refresh data
                                                    } catch (err) {
                                                        alert('Failed to execute action');
                                                    }
                                                }}
                                                className="text-blue-600 hover:text-blue-800 font-medium text-xs ml-2"
                                            >
                                                Auto-Execute
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </Card>
                )}

                {/* Health Forecast Section */}
                {forecast && (
                    <Card className="p-6">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">7-Day Health Forecast & Plausible Illnesses</h2>
                        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
                            {forecast.forecast.map((day, idx) => (
                                <div key={idx} className="border rounded-lg p-3 text-center bg-white shadow-sm hover:shadow-md transition-shadow">
                                    <p className="text-xs font-semibold text-gray-500 mb-2">
                                        {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                                    </p>
                                    <div className={`inline-block px-2 py-1 rounded-full text-xs font-bold mb-2 ${day.aqi_category === 'Good' ? 'bg-green-100 text-green-800' :
                                            day.aqi_category === 'Moderate' ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-red-100 text-red-800'
                                        }`}>
                                        AQI: {day.aqi}
                                    </div>
                                    <div className="text-xs text-left space-y-1">
                                        <p className="font-medium text-gray-700">Risks:</p>
                                        <ul className="list-disc list-inside text-gray-600 text-[10px]">
                                            {day.illnesses.slice(0, 2).map((illness, i) => (
                                                <li key={i} className="truncate" title={illness}>{illness}</li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </Card>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <Card className="p-6">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Referrals</h2>
                        {referrals.length === 0 ? (
                            <p className="text-gray-500 text-sm">No recent referrals</p>
                        ) : (
                            <div className="space-y-3">
                                {referrals.map((referral) => (
                                    <div key={referral.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium text-gray-900">
                                                {referral.direction === 'incoming' ? 'From' : 'To'}: {
                                                    referral.direction === 'incoming' ?
                                                        referral.from_hospital_name : referral.to_hospital_name
                                                }
                                            </p>
                                            <p className="text-xs text-gray-500">
                                                {new Date(referral.created_at).toLocaleString()}
                                            </p>
                                        </div>
                                        <StatusBadge status={referral.status} />
                                    </div>
                                ))}
                            </div>
                        )}
                        <Button
                            variant="outline"
                            className="w-full mt-4"
                            onClick={() => window.location.href = '/hospital/referrals'}
                        >
                            View All Referrals
                        </Button>
                    </Card>

                    <Card className="p-6">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
                        <div className="space-y-3">
                            <Button
                                variant="outline"
                                className="w-full justify-start"
                                onClick={() => window.location.href = '/hospital/capacity'}
                            >
                                📊 Update Capacity
                            </Button>
                            <Button
                                variant="outline"
                                className="w-full justify-start"
                                onClick={() => window.location.href = '/hospital/inventory'}
                            >
                                📦 Manage Inventory
                            </Button>
                            <Button
                                variant="outline"
                                className="w-full justify-start"
                                onClick={() => window.location.href = '/hospital/wallet'}
                            >
                                💰 Wallet & Payouts
                            </Button>
                        </div>
                    </Card>
                </div>
            </div>
        </Layout>
    );
};

export default Dashboard;
