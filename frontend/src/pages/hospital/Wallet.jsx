import React from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';

const Wallet = () => {
    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-900">Hospital Wallet</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="p-6 bg-gradient-to-r from-blue-600 to-blue-800 text-white">
                    <h3 className="text-lg font-medium opacity-90">Current Balance</h3>
                    <p className="mt-2 text-4xl font-bold">₹ 45,250.00</p>
                    <div className="mt-6 flex space-x-3">
                        <Button className="bg-white text-blue-700 hover:bg-gray-100 border-none">Withdraw Funds</Button>
                        <Button variant="outline" className="border-white text-white hover:bg-white/10">View Statement</Button>
                    </div>
                </Card>

                <Card className="p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
                    <div className="grid grid-cols-2 gap-4">
                        <Button variant="outline" className="h-24 flex flex-col items-center justify-center space-y-2">
                            <span className="text-2xl">💳</span>
                            <span>Add Bank Account</span>
                        </Button>
                        <Button variant="outline" className="h-24 flex flex-col items-center justify-center space-y-2">
                            <span className="text-2xl">📄</span>
                            <span>Invoices</span>
                        </Button>
                    </div>
                </Card>
            </div>

            <Card className="p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Transactions</h3>
                <div className="space-y-4">
                    {[1, 2, 3, 4].map((i) => (
                        <div key={i} className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0">
                            <div className="flex items-center space-x-4">
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${i % 2 === 0 ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                                    {i % 2 === 0 ? '↓' : '↑'}
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-gray-900">{i % 2 === 0 ? 'Referral Payment Received' : 'Withdrawal to Bank'}</p>
                                    <p className="text-xs text-gray-500">Oct {25 - i}, 2023</p>
                                </div>
                            </div>
                            <span className={`font-semibold ${i % 2 === 0 ? 'text-green-600' : 'text-gray-900'}`}>
                                {i % 2 === 0 ? '+ ₹ 1,500' : '- ₹ 5,000'}
                            </span>
                        </div>
                    ))}
                </div>
            </Card>
        </div>
    );
};

export default Wallet;
