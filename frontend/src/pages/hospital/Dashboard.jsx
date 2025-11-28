import React from 'react';
import { Card } from '../../components/ui/Card';

const HospitalDashboard = () => {
    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-900">Hospital Dashboard</h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="p-6">
                    <h3 className="text-lg font-medium text-gray-900">Total Patients</h3>
                    <p className="mt-2 text-3xl font-bold text-blue-600">124</p>
                </Card>
                <Card className="p-6">
                    <h3 className="text-lg font-medium text-gray-900">Available Beds</h3>
                    <p className="mt-2 text-3xl font-bold text-green-600">45</p>
                </Card>
                <Card className="p-6">
                    <h3 className="text-lg font-medium text-gray-900">Pending Referrals</h3>
                    <p className="mt-2 text-3xl font-bold text-yellow-600">12</p>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Occupancy Trends</h3>
                    <div className="h-64 bg-gray-100 flex items-center justify-center rounded">
                        <span className="text-gray-500">Chart Placeholder</span>
                    </div>
                </Card>
                <Card className="p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
                    <div className="space-y-4">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="flex items-center justify-between border-b pb-2 last:border-0">
                                <div>
                                    <p className="text-sm font-medium text-gray-900">New Patient Admitted</p>
                                    <p className="text-xs text-gray-500">2 hours ago</p>
                                </div>
                                <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                                    Admitted
                                </span>
                            </div>
                        ))}
                    </div>
                </Card>
            </div>
        </div>
    );
};

export default HospitalDashboard;
