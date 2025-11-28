import React from 'react';
import { Card } from '../../components/ui/Card';

const PatientAlerts = () => {
    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-900">Health Alerts</h1>

            <div className="grid gap-4">
                <Card className="p-4 border-l-4 border-red-500">
                    <div className="flex items-start">
                        <div className="flex-shrink-0">
                            <span className="text-2xl">⚠️</span>
                        </div>
                        <div className="ml-3">
                            <h3 className="text-lg font-medium text-red-800">High Pollution Warning</h3>
                            <p className="mt-1 text-sm text-red-700">
                                Air Quality Index (AQI) is currently 350 (Severe). Avoid outdoor activities if you have respiratory issues.
                            </p>
                        </div>
                    </div>
                </Card>

                <Card className="p-4 border-l-4 border-yellow-500">
                    <div className="flex items-start">
                        <div className="flex-shrink-0">
                            <span className="text-2xl">🦠</span>
                        </div>
                        <div className="ml-3">
                            <h3 className="text-lg font-medium text-yellow-800">Flu Season Alert</h3>
                            <p className="mt-1 text-sm text-yellow-700">
                                Viral fever cases are rising in your area. Ensure you are vaccinated and maintain hygiene.
                            </p>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    );
};

export default PatientAlerts;
