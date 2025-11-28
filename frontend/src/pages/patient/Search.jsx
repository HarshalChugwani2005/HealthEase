import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';

const HospitalSearch = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [hospitals, setHospitals] = useState([]);

    const handleSearch = (e) => {
        e.preventDefault();
        // Mock search results
        setHospitals([
            { id: 1, name: 'City General Hospital', distance: '2.5 km', load: 'High', beds: 12 },
            { id: 2, name: 'St. Mary\'s Clinic', distance: '4.1 km', load: 'Low', beds: 45 },
            { id: 3, name: 'Sunrise Health Center', distance: '5.8 km', load: 'Moderate', beds: 23 },
        ]);
    };

    return (
        <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm">
                <h1 className="text-2xl font-bold text-gray-900 mb-4">Find Nearby Hospitals</h1>
                <form onSubmit={handleSearch} className="flex gap-4">
                    <input
                        type="text"
                        placeholder="Search by name, specialty, or location..."
                        className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                    <Button type="submit">Search</Button>
                </form>
            </div>

            <div className="grid gap-6">
                {hospitals.map((hospital) => (
                    <Card key={hospital.id} className="p-6 hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start">
                            <div>
                                <h3 className="text-xl font-semibold text-gray-900">{hospital.name}</h3>
                                <p className="text-gray-500 mt-1">Distance: {hospital.distance}</p>
                                <div className="flex items-center gap-4 mt-2">
                                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${hospital.load === 'High' ? 'bg-red-100 text-red-800' :
                                            hospital.load === 'Moderate' ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-green-100 text-green-800'
                                        }`}>
                                        {hospital.load} Load
                                    </span>
                                    <span className="text-sm text-gray-600">{hospital.beds} beds available</span>
                                </div>
                            </div>
                            <Button>Book Referral</Button>
                        </div>
                    </Card>
                ))}
            </div>
        </div>
    );
};

export default HospitalSearch;
