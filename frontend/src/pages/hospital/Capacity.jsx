import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import api from '../../lib/api';

const Capacity = () => {
    const [capacity, setCapacity] = useState({
        total_beds: 0,
        available_beds: 0,
        icu_beds: 0,
        available_icu_beds: 0,
        ventilators: 0,
        available_ventilators: 0
    });
    const [loading, setLoading] = useState(true);
    const [updating, setUpdating] = useState(false);
    const [success, setSuccess] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        fetchCapacity();
    }, []);

    const fetchCapacity = async () => {
        try {
            const response = await api.get('/api/capacity/current');
            setCapacity(response.data);
        } catch (err) {
            setError('Error fetching capacity');
        } finally {
            setLoading(false);
        }
    };

    const handleUpdate = async (e) => {
        e.preventDefault();
        setUpdating(true);
        setError('');
        setSuccess('');

        try {
            await api.put('/api/capacity/update', capacity);
            setSuccess('Capacity updated successfully');
            fetchCapacity();
        } catch (err) {
            console.error('Update capacity error:', err);
            const errorMessage = err.response?.data?.detail || err.message || 'Error updating capacity';
            setError(typeof errorMessage === 'object' ? JSON.stringify(errorMessage) : errorMessage);
        } finally {
            setUpdating(false);
        }
    };

    const handleQuickUpdate = async (field, change) => {
        try {
            await api.post('/api/capacity/quick-update', {
                field: field,
                change: change
            });
            fetchCapacity();
            setSuccess(`${field} ${change > 0 ? 'increased' : 'decreased'}`);
            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Error updating');
        }
    };

    const occupancyPercentage = capacity.total_beds > 0 ?
        ((capacity.total_beds - capacity.available_beds) / capacity.total_beds * 100).toFixed(1) : 0;

    if (loading) {
        return (
            <div className="space-y-6">
                <h1 className="text-2xl font-bold text-gray-900">Capacity Management</h1>
                <Card className="p-6"><p className="text-gray-600">Loading...</p></Card>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-900">Capacity Management</h1>

            <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Current Status</h2>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="p-4 bg-blue-50 rounded-lg">
                        <p className="text-sm text-gray-600">Total Beds</p>
                        <p className="text-3xl font-bold text-blue-600">{capacity.total_beds}</p>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg">
                        <p className="text-sm text-gray-600">Available Beds</p>
                        <p className="text-3xl font-bold text-green-600">{capacity.available_beds}</p>
                    </div>
                    <div className="p-4 bg-purple-50 rounded-lg">
                        <p className="text-sm text-gray-600">ICU Beds</p>
                        <p className="text-3xl font-bold text-purple-600">{capacity.icu_beds}</p>
                    </div>
                    <div className="p-4 bg-orange-50 rounded-lg">
                        <p className="text-sm text-gray-600">Ventilators</p>
                        <p className="text-3xl font-bold text-orange-600">{capacity.ventilators}</p>
                    </div>
                </div>

                <div className="mb-6">
                    <p className="text-sm text-gray-600 mb-2">Occupancy Rate</p>
                    <div className="w-full bg-gray-200 rounded-full h-4">
                        <div
                            className={`h-4 rounded-full ${occupancyPercentage >= 90 ? 'bg-red-600' :
                                occupancyPercentage >= 75 ? 'bg-orange-600' :
                                    occupancyPercentage >= 50 ? 'bg-yellow-600' :
                                        'bg-green-600'
                                }`}
                            style={{ width: `${occupancyPercentage}%` }}
                        ></div>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{occupancyPercentage}% occupied</p>
                </div>

                {success && (
                    <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
                        <p className="text-sm text-green-700">{success}</p>
                    </div>
                )}

                {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                        <p className="text-sm text-red-700">{error}</p>
                    </div>
                )}
            </Card>

            <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <p className="text-sm font-medium text-gray-700 mb-3">Available Beds</p>
                        <div className="flex items-center gap-3">
                            <Button
                                variant="outline"
                                onClick={() => handleQuickUpdate('available_beds', -1)}
                                disabled={capacity.available_beds <= 0}
                            >
                                - 1
                            </Button>
                            <span className="text-2xl font-bold text-gray-900 min-w-[60px] text-center">
                                {capacity.available_beds}
                            </span>
                            <Button
                                variant="outline"
                                onClick={() => handleQuickUpdate('available_beds', 1)}
                                disabled={capacity.available_beds >= capacity.total_beds}
                            >
                                + 1
                            </Button>
                        </div>
                    </div>

                    <div>
                        <p className="text-sm font-medium text-gray-700 mb-3">ICU Beds</p>
                        <div className="flex items-center gap-3">
                            <Button
                                variant="outline"
                                onClick={() => handleQuickUpdate('icu_beds', -1)}
                                disabled={capacity.icu_beds <= 0}
                            >
                                - 1
                            </Button>
                            <span className="text-2xl font-bold text-gray-900 min-w-[60px] text-center">
                                {capacity.icu_beds}
                            </span>
                            <Button
                                variant="outline"
                                onClick={() => handleQuickUpdate('icu_beds', 1)}
                            >
                                + 1
                            </Button>
                        </div>
                    </div>

                    <div>
                        <p className="text-sm font-medium text-gray-700 mb-3">Ventilators</p>
                        <div className="flex items-center gap-3">
                            <Button
                                variant="outline"
                                onClick={() => handleQuickUpdate('ventilators', -1)}
                                disabled={capacity.ventilators <= 0}
                            >
                                - 1
                            </Button>
                            <span className="text-2xl font-bold text-gray-900 min-w-[60px] text-center">
                                {capacity.ventilators}
                            </span>
                            <Button
                                variant="outline"
                                onClick={() => handleQuickUpdate('ventilators', 1)}
                            >
                                + 1
                            </Button>
                        </div>
                    </div>
                </div>
            </Card>

            <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Update Full Capacity</h2>
                <form onSubmit={handleUpdate} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Total Beds
                            </label>
                            <input
                                type="number"
                                value={capacity.total_beds}
                                onChange={(e) => setCapacity({ ...capacity, total_beds: parseInt(e.target.value) || 0 })}
                                className="w-full rounded-md border-gray-300"
                                min="0"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Available Beds
                            </label>
                            <input
                                type="number"
                                value={capacity.available_beds}
                                onChange={(e) => setCapacity({ ...capacity, available_beds: parseInt(e.target.value) || 0 })}
                                className="w-full rounded-md border-gray-300"
                                min="0"
                                max={capacity.total_beds}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                ICU Beds
                            </label>
                            <input
                                type="number"
                                value={capacity.icu_beds}
                                onChange={(e) => setCapacity({ ...capacity, icu_beds: parseInt(e.target.value) || 0 })}
                                className="w-full rounded-md border-gray-300"
                                min="0"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Available ICU Beds
                            </label>
                            <input
                                type="number"
                                value={capacity.available_icu_beds}
                                onChange={(e) => setCapacity({ ...capacity, available_icu_beds: parseInt(e.target.value) || 0 })}
                                className="w-full rounded-md border-gray-300"
                                min="0"
                                max={capacity.icu_beds}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Ventilators
                            </label>
                            <input
                                type="number"
                                value={capacity.ventilators}
                                onChange={(e) => setCapacity({ ...capacity, ventilators: parseInt(e.target.value) || 0 })}
                                className="w-full rounded-md border-gray-300"
                                min="0"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Available Ventilators
                            </label>
                            <input
                                type="number"
                                value={capacity.available_ventilators}
                                onChange={(e) => setCapacity({ ...capacity, available_ventilators: parseInt(e.target.value) || 0 })}
                                className="w-full rounded-md border-gray-300"
                                min="0"
                                max={capacity.ventilators}
                            />
                        </div>
                    </div>

                    <Button type="submit" disabled={updating} className="w-full">
                        {updating ? 'Updating...' : 'Update Capacity'}
                    </Button>
                </form>
            </Card>
        </div >
    );
};

export default Capacity;
