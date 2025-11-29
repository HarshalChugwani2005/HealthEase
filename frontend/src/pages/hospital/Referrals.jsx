import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import api from '../../lib/api';

const Referrals = () => {
    const [referrals, setReferrals] = useState([]);
    const [filter, setFilter] = useState('all');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchReferrals();
    }, [filter]);

    const fetchReferrals = async () => {
        try {
            const response = await api.get('/api/referrals/hospital-referrals', {
                params: { limit: 50 }
            });
            let data = response.data.referrals || [];
            
            if (filter !== 'all') {
                data = data.filter(r => r.status === filter);
            }
            
            setReferrals(data);
        } catch (err) {
            console.error('Referrals error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleAcceptReferral = async (referralId) => {
        try {
            await api.post(`/api/referrals/${referralId}/accept`);
            fetchReferrals();
        } catch (err) {
            alert(err.response?.data?.detail || 'Error accepting referral');
        }
    };

    const handleRejectReferral = async (referralId) => {
        const reason = prompt('Please provide a reason for rejection:');
        if (!reason) return;

        try {
            await api.post(`/api/referrals/${referralId}/reject`, { reason });
            fetchReferrals();
        } catch (err) {
            alert(err.response?.data?.detail || 'Error rejecting referral');
        }
    };

    const getStatusColor = (status) => {
        const colors = {
            pending: 'bg-yellow-100 text-yellow-800',
            accepted: 'bg-green-100 text-green-800',
            rejected: 'bg-red-100 text-red-800',
            completed: 'bg-blue-100 text-blue-800'
        };
        return colors[status] || 'bg-gray-100 text-gray-800';
    };

    const getDirectionBadge = (direction) => {
        return direction === 'incoming' ? (
            <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                Incoming
            </span>
        ) : (
            <span className="px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
                Outgoing
            </span>
        );
    };

    if (loading) {
        return (
            <div className="space-y-6">
                <h1 className="text-2xl font-bold text-gray-900">Referrals Management</h1>
                <Card className="p-6"><p className="text-gray-600">Loading...</p></Card>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-900">Referrals Management</h1>
                <Button onClick={fetchReferrals} variant="outline">Refresh</Button>
            </div>

            <Card className="p-4">
                <div className="flex gap-2 flex-wrap">
                    <Button 
                        variant={filter === 'all' ? 'primary' : 'outline'}
                        onClick={() => setFilter('all')}
                        size="sm"
                    >
                        All ({referrals.length})
                    </Button>
                    <Button 
                        variant={filter === 'pending' ? 'primary' : 'outline'}
                        onClick={() => setFilter('pending')}
                        size="sm"
                    >
                        Pending
                    </Button>
                    <Button 
                        variant={filter === 'accepted' ? 'primary' : 'outline'}
                        onClick={() => setFilter('accepted')}
                        size="sm"
                    >
                        Accepted
                    </Button>
                    <Button 
                        variant={filter === 'rejected' ? 'primary' : 'outline'}
                        onClick={() => setFilter('rejected')}
                        size="sm"
                    >
                        Rejected
                    </Button>
                    <Button 
                        variant={filter === 'completed' ? 'primary' : 'outline'}
                        onClick={() => setFilter('completed')}
                        size="sm"
                    >
                        Completed
                    </Button>
                </div>
            </Card>

            {referrals.length === 0 ? (
                <Card className="p-12 text-center">
                    <p className="text-gray-500">No referrals found</p>
                </Card>
            ) : (
                <div className="space-y-4">
                    {referrals.map((referral) => (
                        <Card key={referral.id} className="p-6">
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex items-center gap-3">
                                    {getDirectionBadge(referral.direction)}
                                    <div>
                                        <h3 className="font-semibold text-lg text-gray-900">
                                            {referral.direction === 'incoming' ? 
                                                `From: ${referral.from_hospital_name}` : 
                                                `To: ${referral.to_hospital_name}`}
                                        </h3>
                                        <p className="text-sm text-gray-600">
                                            Patient: {referral.patient_name || 'N/A'}
                                        </p>
                                    </div>
                                </div>
                                <span className={`px-3 py-1 text-xs font-semibold rounded-full ${getStatusColor(referral.status)}`}>
                                    {referral.status.toUpperCase()}
                                </span>
                            </div>

                            {referral.reason && (
                                <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                                    <p className="text-sm text-gray-700">
                                        <span className="font-medium">Reason:</span> {referral.reason}
                                    </p>
                                </div>
                            )}

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                                <div>
                                    <p className="text-gray-600">Referral ID</p>
                                    <p className="font-mono text-xs">{referral.id.substring(0, 8)}...</p>
                                </div>
                                <div>
                                    <p className="text-gray-600">Created</p>
                                    <p className="font-medium">{new Date(referral.created_at).toLocaleDateString()}</p>
                                </div>
                                <div>
                                    <p className="text-gray-600">Payment</p>
                                    <p className="font-medium">
                                        {referral.payment_status === 'completed' ? '✓ Paid' : 'Pending'}
                                    </p>
                                </div>
                                {referral.hospital_earning && (
                                    <div>
                                        <p className="text-gray-600">Earning</p>
                                        <p className="font-medium text-green-600">₹{referral.hospital_earning.toFixed(2)}</p>
                                    </div>
                                )}
                            </div>

                            {referral.direction === 'incoming' && referral.status === 'pending' && (
                                <div className="flex gap-3 mt-4">
                                    <Button 
                                        onClick={() => handleAcceptReferral(referral.id)}
                                        className="flex-1 bg-green-600 hover:bg-green-700"
                                    >
                                        Accept Referral
                                    </Button>
                                    <Button 
                                        onClick={() => handleRejectReferral(referral.id)}
                                        variant="outline"
                                        className="flex-1 text-red-600 border-red-600 hover:bg-red-50"
                                    >
                                        Reject
                                    </Button>
                                </div>
                            )}

                            {referral.status === 'rejected' && referral.rejection_reason && (
                                <div className="mt-4 p-3 bg-red-50 rounded-lg">
                                    <p className="text-sm text-red-800">
                                        <span className="font-medium">Rejection Reason:</span> {referral.rejection_reason}
                                    </p>
                                </div>
                            )}

                            {referral.status === 'accepted' && referral.direction === 'incoming' && (
                                <div className="mt-4 p-3 bg-green-50 rounded-lg">
                                    <p className="text-sm text-green-800">
                                        ✓ Referral accepted. Please coordinate with the referring hospital for patient transfer.
                                    </p>
                                </div>
                            )}
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Referrals;
