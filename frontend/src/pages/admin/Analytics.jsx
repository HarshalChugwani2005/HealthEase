import React from 'react';
import { Card } from '../../components/ui/Card';

const AdminAnalytics = () => {
    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-900">System Analytics</h1>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <Card className="p-6">
                    <h3 className="text-sm font-medium text-gray-500">Total Hospitals</h3>
                    <p className="mt-2 text-3xl font-bold text-gray-900">156</p>
                    <span className="text-green-600 text-sm font-medium">↑ 12% from last month</span>
                </Card>
                <Card className="p-6">
                    <h3 className="text-sm font-medium text-gray-500">Total Patients</h3>
                    <p className="mt-2 text-3xl font-bold text-gray-900">2,450</p>
                    <span className="text-green-600 text-sm font-medium">↑ 8% from last month</span>
                </Card>
                <Card className="p-6">
                    <h3 className="text-sm font-medium text-gray-500">Total Revenue</h3>
                    <p className="mt-2 text-3xl font-bold text-gray-900">₹ 12.5L</p>
                    <span className="text-green-600 text-sm font-medium">↑ 15% from last month</span>
                </Card>
                <Card className="p-6">
                    <h3 className="text-sm font-medium text-gray-500">Active Referrals</h3>
                    <p className="mt-2 text-3xl font-bold text-gray-900">85</p>
                    <span className="text-red-600 text-sm font-medium">↓ 2% from last month</span>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Revenue Growth</h3>
                    <div className="h-64 bg-gray-100 flex items-center justify-center rounded">
                        <span className="text-gray-500">Chart Placeholder</span>
                    </div>
                </Card>
                <Card className="p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">User Distribution</h3>
                    <div className="h-64 bg-gray-100 flex items-center justify-center rounded">
                        <span className="text-gray-500">Chart Placeholder</span>
                    </div>
                </Card>
            </div>
        </div>
    );
};

export default AdminAnalytics;
