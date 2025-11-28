import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';

const ReferralFlow = () => {
    const [step, setStep] = useState(1);

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <h1 className="text-2xl font-bold text-gray-900">Create New Referral</h1>

            <Card className="p-8">
                {step === 1 && (
                    <div className="space-y-4">
                        <h2 className="text-xl font-semibold">Step 1: Patient Details</h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Condition Description</label>
                                <textarea className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" rows="3"></textarea>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Urgency Level</label>
                                <select className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                                    <option>Low</option>
                                    <option>Moderate</option>
                                    <option>High</option>
                                    <option>Critical</option>
                                </select>
                            </div>
                        </div>
                        <div className="flex justify-end pt-4">
                            <Button onClick={() => setStep(2)}>Next: Select Hospital</Button>
                        </div>
                    </div>
                )}

                {step === 2 && (
                    <div className="space-y-4">
                        <h2 className="text-xl font-semibold">Step 2: Payment</h2>
                        <div className="bg-gray-50 p-4 rounded-md">
                            <p className="text-sm text-gray-600">Referral Fee</p>
                            <p className="text-2xl font-bold text-gray-900">₹ 500.00</p>
                        </div>
                        <div className="flex justify-between pt-4">
                            <Button variant="outline" onClick={() => setStep(1)}>Back</Button>
                            <Button onClick={() => alert('Payment Integration Placeholder')}>Pay & Create Referral</Button>
                        </div>
                    </div>
                )}
            </Card>
        </div>
    );
};

export default ReferralFlow;
