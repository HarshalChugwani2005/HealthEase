import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';

const Referrals = () => {
    const [referrals] = useState([
        { id: 1, patient: 'John Doe', from: 'City Clinic', condition: 'Critical', status: 'Pending', date: '2023-10-25' },
        { id: 2, patient: 'Jane Smith', from: 'Community Health', condition: 'Stable', status: 'Accepted', date: '2023-10-24' },
    ]);

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-900">Incoming Referrals</h1>

            <div className="grid gap-6">
                {referrals.map((referral) => (
                    <Card key={referral.id} className="p-6">
                        <div className="flex justify-between items-start">
                            <div>
                                <div className="flex items-center space-x-3">
                                    <h3 className="text-lg font-medium text-gray-900">{referral.patient}</h3>
                                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${referral.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
                                        }`}>
                                        {referral.status}
                                    </span>
                                </div>
                                <p className="text-sm text-gray-500 mt-1">Referred from: {referral.from}</p>
                                <p className="text-sm text-gray-500">Condition: {referral.condition}</p>
                                <p className="text-sm text-gray-500">Date: {referral.date}</p>
                            </div>
                            <div className="flex space-x-3">
                                {referral.status === 'Pending' && (
                                    <>
                                        <Button variant="outline" className="text-red-600 border-red-600 hover:bg-red-50">Reject</Button>
                                        <Button className="bg-green-600 hover:bg-green-700">Accept</Button>
                                    </>
                                )}
                                <Button variant="outline">View Details</Button>
                            </div>
                        </div>
                    </Card>
                ))}
            </div>
        </div>
    );
};

export default Referrals;
