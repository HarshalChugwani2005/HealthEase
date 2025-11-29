import React, { useEffect, useState } from 'react';
import { Card } from '../../components/ui/Card';
import api from '../../lib/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const AdminAnalytics = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await api.get('/api/admin/analytics');
                setStats(response.data);
            } catch (error) {
                console.error('Failed to fetch analytics:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
        // Real-time polling every 30 seconds
        const interval = setInterval(fetchStats, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return <div className="p-6">Loading analytics...</div>;
    }

    if (!stats) {
        return <div className="p-6">Failed to load analytics.</div>;
    }

    const hospitalData = [
        { name: 'Free Tier', value: stats.hospitals.free_tier },
        { name: 'Paid Tier', value: stats.hospitals.paid_tier },
    ];

    const referralData = [
        { name: 'Completed', value: stats.referrals.completed },
        { name: 'Pending', value: stats.referrals.pending },
    ];

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-900">System Analytics</h1>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <Card className="p-6">
                    <h3 className="text-sm font-medium text-gray-500">Total Hospitals</h3>
                    <p className="mt-2 text-3xl font-bold text-gray-900">{stats.overview.total_hospitals}</p>
                    <span className="text-green-600 text-sm font-medium">{stats.hospitals.verified} Verified</span>
                </Card>
                <Card className="p-6">
                    <h3 className="text-sm font-medium text-gray-500">Total Patients</h3>
                    <p className="mt-2 text-3xl font-bold text-gray-900">{stats.overview.total_patients}</p>
                    <span className="text-green-600 text-sm font-medium">Active Users</span>
                </Card>
                <Card className="p-6">
                    <h3 className="text-sm font-medium text-gray-500">Total Referrals</h3>
                    <p className="mt-2 text-3xl font-bold text-gray-900">{stats.overview.total_referrals}</p>
                    <span className="text-green-600 text-sm font-medium">{stats.referrals.completion_rate}% Completion</span>
                </Card>
                <Card className="p-6">
                    <h3 className="text-sm font-medium text-gray-500">Pending Referrals</h3>
                    <p className="mt-2 text-3xl font-bold text-gray-900">{stats.referrals.pending}</p>
                    <span className="text-yellow-600 text-sm font-medium">Action Required</span>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Hospital Distribution</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={hospitalData}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                    outerRadius={80}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {hospitalData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </Card>
                <Card className="p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Referral Status</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart
                                data={referralData}
                                margin={{
                                    top: 5,
                                    right: 30,
                                    left: 20,
                                    bottom: 5,
                                }}
                            >
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="value" fill="#82ca9d" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </Card>
            </div>
        </div>
    );
};

export default AdminAnalytics;
