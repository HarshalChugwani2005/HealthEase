import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import api from '../../lib/api';

const PatientAlerts = () => {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchAlerts();
    }, []);

    const fetchAlerts = async () => {
        try {
            // In a real app, we would get the user's location here
            const response = await api.get('/api/alerts/all-alerts', {
                params: { city: 'Delhi', state: 'Delhi' }
            });
            setAlerts(response.data.alerts || []);
        } catch (err) {
            console.error('Error fetching alerts:', err);
            setError('Failed to load health alerts');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="p-6">Loading health alerts...</div>;
    }

    if (error) {
        return <div className="p-6 text-red-600">{error}</div>;
    }

    if (alerts.length === 0) {
        return (
            <div className="space-y-6">
                <h1 className="text-2xl font-bold text-gray-900">Health Alerts</h1>
                <Card className="p-6">
                    <p className="text-gray-500">No active health alerts for your area.</p>
                </Card>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-900">Health Alerts</h1>

            <div className="grid gap-4">
                {alerts.map((alert) => (
                    <Card 
                        key={alert.id} 
                        className={`p-4 border-l-4 ${
                            alert.severity === 'critical' ? 'border-red-600 bg-red-50' :
                            alert.severity === 'high' ? 'border-orange-500 bg-orange-50' :
                            alert.severity === 'medium' ? 'border-yellow-500 bg-yellow-50' :
                            'border-blue-500 bg-blue-50'
                        }`}
                    >
                        <div className="flex items-start">
                            <div className="flex-shrink-0 text-2xl mr-3">
                                {alert.type === 'pollution' ? '🌫️' :
                                 alert.type === 'festival' ? '🎉' :
                                 alert.type === 'epidemic' ? '🦠' : '⚠️'}
                            </div>
                            <div className="flex-1">
                                <h3 className={`text-lg font-medium ${
                                    alert.severity === 'critical' ? 'text-red-800' :
                                    alert.severity === 'high' ? 'text-orange-800' :
                                    alert.severity === 'medium' ? 'text-yellow-800' :
                                    'text-blue-800'
                                }`}>
                                    {alert.title}
                                </h3>
                                <p className={`mt-1 text-sm ${
                                    alert.severity === 'critical' ? 'text-red-700' :
                                    alert.severity === 'high' ? 'text-orange-700' :
                                    alert.severity === 'medium' ? 'text-yellow-700' :
                                    'text-blue-700'
                                }`}>
                                    {alert.message}
                                </p>
                                {alert.recommendations && (
                                    <div className="mt-3">
                                        <p className="text-xs font-semibold mb-1 opacity-75">Recommendations:</p>
                                        <ul className="list-disc list-inside text-sm space-y-1 opacity-90">
                                            {alert.recommendations.map((rec, idx) => (
                                                <li key={idx}>{rec}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </div>
                    </Card>
                ))}
            </div>
        </div>
    );
};

export default PatientAlerts;
