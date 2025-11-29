import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import api from '../../lib/api';

const Wallet = () => {
    const [balance, setBalance] = useState(0);
    const [transactions, setTransactions] = useState([]);
    const [payoutRequests, setPayoutRequests] = useState([]);
    const [showPayoutForm, setShowPayoutForm] = useState(false);
    const [loading, setLoading] = useState(true);
    const [payoutForm, setPayoutForm] = useState({
        amount: '',
        bank_account_number: '',
        ifsc_code: '',
        account_holder_name: ''
    });

    useEffect(() => {
        fetchWalletData();
    }, []);

    const fetchWalletData = async () => {
        try {
            const [balanceRes, transactionsRes, payoutsRes] = await Promise.all([
                api.get('/api/wallet/balance'),
                api.get('/api/wallet/transactions', { params: { limit: 20 } }),
                api.get('/api/wallet/payout-requests')
            ]);

            setBalance(balanceRes.data.balance);
            setTransactions(transactionsRes.data.transactions || []);
            setPayoutRequests(payoutsRes.data.payout_requests || []);
        } catch (err) {
            console.error('Wallet error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleRequestPayout = async (e) => {
        e.preventDefault();
        try {
            await api.post('/api/wallet/request-payout', {
                ...payoutForm,
                amount: parseFloat(payoutForm.amount)
            });
            setPayoutForm({ amount: '', bank_account_number: '', ifsc_code: '', account_holder_name: '' });
            setShowPayoutForm(false);
            fetchWalletData();
            alert('Payout request submitted successfully');
        } catch (err) {
            alert(err.response?.data?.detail || 'Error requesting payout');
        }
    };

    const getTypeColor = (type) => {
        const colors = {
            referral_earning: 'bg-green-100 text-green-800',
            payout: 'bg-blue-100 text-blue-800',
            refund: 'bg-orange-100 text-orange-800',
            adjustment: 'bg-purple-100 text-purple-800'
        };
        return colors[type] || 'bg-gray-100 text-gray-800';
    };

    const getStatusColor = (status) => {
        const colors = {
            pending: 'bg-yellow-100 text-yellow-800',
            approved: 'bg-green-100 text-green-800',
            rejected: 'bg-red-100 text-red-800',
            completed: 'bg-blue-100 text-blue-800'
        };
        return colors[status] || 'bg-gray-100 text-gray-800';
    };

    if (loading) {
        return (
            <div className="space-y-6">
                <h1 className="text-2xl font-bold text-gray-900">Wallet & Payouts</h1>
                <Card className="p-6"><p className="text-gray-600">Loading...</p></Card>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-900">Wallet & Payouts</h1>
                <Button onClick={fetchWalletData} variant="outline">Refresh</Button>
            </div>

            <Card className="p-6 bg-gradient-to-r from-green-50 to-blue-50">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-sm text-gray-600">Available Balance</p>
                        <p className="text-4xl font-bold text-green-600 mt-1">₹{balance.toFixed(2)}</p>
                        <p className="text-xs text-gray-500 mt-1">Minimum payout: ₹100</p>
                    </div>
                    <Button 
                        onClick={() => setShowPayoutForm(!showPayoutForm)}
                        disabled={balance < 100}
                    >
                        {showPayoutForm ? 'Cancel' : 'Request Payout'}
                    </Button>
                </div>
            </Card>

            {showPayoutForm && (
                <Card className="p-6">
                    <h2 className="text-lg font-semibold mb-4">Request Payout</h2>
                    <form onSubmit={handleRequestPayout} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Amount (₹)</label>
                            <input
                                type="number"
                                value={payoutForm.amount}
                                onChange={(e) => setPayoutForm({...payoutForm, amount: e.target.value})}
                                className="w-full rounded-md border-gray-300"
                                min="100"
                                max={balance}
                                step="0.01"
                                required
                            />
                            <p className="text-xs text-gray-500 mt-1">
                                Max: ₹{balance.toFixed(2)}
                            </p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Account Holder Name</label>
                            <input
                                type="text"
                                value={payoutForm.account_holder_name}
                                onChange={(e) => setPayoutForm({...payoutForm, account_holder_name: e.target.value})}
                                className="w-full rounded-md border-gray-300"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Bank Account Number</label>
                            <input
                                type="text"
                                value={payoutForm.bank_account_number}
                                onChange={(e) => setPayoutForm({...payoutForm, bank_account_number: e.target.value})}
                                className="w-full rounded-md border-gray-300"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">IFSC Code</label>
                            <input
                                type="text"
                                value={payoutForm.ifsc_code}
                                onChange={(e) => setPayoutForm({...payoutForm, ifsc_code: e.target.value})}
                                className="w-full rounded-md border-gray-300"
                                placeholder="e.g., SBIN0001234"
                                required
                            />
                        </div>

                        <Button type="submit" className="w-full">Submit Payout Request</Button>
                    </form>
                </Card>
            )}

            <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Payout Requests</h2>
                {payoutRequests.length === 0 ? (
                    <p className="text-gray-500 text-sm text-center py-4">No payout requests</p>
                ) : (
                    <div className="space-y-3">
                        {payoutRequests.map((request) => (
                            <div key={request.id} className="p-4 bg-gray-50 rounded-lg">
                                <div className="flex justify-between items-start mb-2">
                                    <div>
                                        <p className="font-semibold text-lg">₹{request.amount.toFixed(2)}</p>
                                        <p className="text-xs text-gray-600">
                                            {new Date(request.created_at).toLocaleString()}
                                        </p>
                                    </div>
                                    <span className={`px-3 py-1 text-xs font-semibold rounded-full ${getStatusColor(request.status)}`}>
                                        {request.status.toUpperCase()}
                                    </span>
                                </div>
                                <div className="text-xs text-gray-600">
                                    <p>Account: {request.bank_account_number}</p>
                                    <p>IFSC: {request.ifsc_code}</p>
                                    {request.processed_at && (
                                        <p className="mt-1">Processed: {new Date(request.processed_at).toLocaleString()}</p>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </Card>

            <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Transaction History</h2>
                {transactions.length === 0 ? (
                    <p className="text-gray-500 text-sm text-center py-4">No transactions yet</p>
                ) : (
                    <div className="space-y-2">
                        {transactions.map((txn) => (
                            <div key={txn.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                <div>
                                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getTypeColor(txn.type)}`}>
                                        {txn.type.replace('_', ' ').toUpperCase()}
                                    </span>
                                    <p className="text-xs text-gray-600 mt-1">
                                        {new Date(txn.created_at).toLocaleString()}
                                    </p>
                                    {txn.description && (
                                        <p className="text-xs text-gray-500 mt-1">{txn.description}</p>
                                    )}
                                </div>
                                <div className="text-right">
                                    <p className={`font-semibold ${txn.amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {txn.amount >= 0 ? '+' : ''}₹{txn.amount.toFixed(2)}
                                    </p>
                                    <p className="text-xs text-gray-500">
                                        Balance: ₹{txn.balance_after.toFixed(2)}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </Card>
        </div>
    );
};

export default Wallet;
