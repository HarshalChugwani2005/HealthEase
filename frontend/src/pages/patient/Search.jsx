import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { ReviewModal } from '../../components/ui/ReviewModal';
import AppointmentBooking from '../../components/ui/AppointmentBooking';
import api from '../../lib/api';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix Leaflet icon issue
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// Component to update map center
const MapUpdater = ({ center }) => {
    const map = useMap();
    useEffect(() => {
        if (center) {
            map.setView(center, 13);
        }
    }, [center, map]);
    return null;
};

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';

const HospitalSearch = () => {
    const [searchParams, setSearchParams] = useState({
        latitude: '',
        longitude: '',
        city: 'Delhi',
        max_distance_km: 50,
        specialization: '',
        has_beds: true,
        has_icu: false,
        has_ventilator: false,
        sort_by: 'distance'
    });
    const [hospitals, setHospitals] = useState([]);
    const [specializations, setSpecializations] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [useGPS, setUseGPS] = useState(true);
    const [reviewHospital, setReviewHospital] = useState(null);
    const [bookingHospital, setBookingHospital] = useState(null);

    useEffect(() => {
        fetchSpecializations();
        if (useGPS) {
            getLocation();
        }
    }, []);

    useEffect(() => {
        // Auto-search when GPS coordinates are obtained
        if (useGPS && searchParams.latitude && searchParams.longitude && !loading) {
            console.log('Auto-searching with coordinates:', searchParams.latitude, searchParams.longitude);
        }
    }, [searchParams.latitude, searchParams.longitude]);

    const getLocation = async () => {
        setLoading(true);
        setError('');

        // First try: HTML5 Geolocation API (requires HTTPS)
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    console.log('Location obtained via browser geolocation:', position.coords);
                    setSearchParams(prev => ({
                        ...prev,
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    }));
                    setLoading(false);
                    // Auto-search after getting location
                    setTimeout(() => {
                        handleSearch({ preventDefault: () => { } });
                    }, 500);
                },
                async (error) => {
                    console.error("Browser geolocation error:", error.message);

                    // Second try: Google Geolocation API as fallback
                    if (GOOGLE_MAPS_API_KEY) {
                        try {
                            const location = await getLocationViaGoogle();
                            if (location) {
                                console.log('Location obtained via Google API:', location);
                                setSearchParams(prev => ({
                                    ...prev,
                                    latitude: location.lat,
                                    longitude: location.lng
                                }));
                                setLoading(false);
                                // Auto-search after getting location
                                setTimeout(() => {
                                    handleSearch({ preventDefault: () => { } });
                                }, 500);
                                return;
                            }
                        } catch (googleError) {
                            console.error("Google geolocation error:", googleError);
                        }
                    }

                    // Third try: IP-based geolocation as last resort
                    try {
                        const ipLocation = await getLocationViaIP();
                        if (ipLocation) {
                            console.log('Location obtained via IP:', ipLocation);
                            setSearchParams(prev => ({
                                ...prev,
                                latitude: ipLocation.lat,
                                longitude: ipLocation.lng
                            }));
                            setError('Using approximate location based on your IP address. For better accuracy, please enable location permissions.');
                            setLoading(false);
                            // Auto-search after getting location
                            setTimeout(() => {
                                handleSearch({ preventDefault: () => { } });
                            }, 500);
                            return;
                        }
                    } catch (ipError) {
                        console.error("IP geolocation error:", ipError);
                    }

                    // All methods failed
                    setError("Unable to get your location. Please enable location permissions or enter your city manually.");
                    setUseGPS(false);
                    setLoading(false);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        } else {
            setError("Geolocation is not supported by your browser. Please enter your city manually.");
            setUseGPS(false);
            setLoading(false);
        }
    };

    const getLocationViaGoogle = async () => {
        try {
            const response = await fetch(`https://www.googleapis.com/geolocation/v1/geolocate?key=${GOOGLE_MAPS_API_KEY}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    considerIp: true
                })
            });

            if (!response.ok) {
                throw new Error('Google Geolocation API request failed');
            }

            const data = await response.json();
            return {
                lat: data.location.lat,
                lng: data.location.lng
            };
        } catch (error) {
            console.error('Google Geolocation API error:', error);
            return null;
        }
    };

    const getLocationViaIP = async () => {
        try {
            // Using ipapi.co free service (no API key required)
            const response = await fetch('https://ipapi.co/json/');
            if (!response.ok) {
                throw new Error('IP geolocation request failed');
            }

            const data = await response.json();
            return {
                lat: data.latitude,
                lng: data.longitude,
                city: data.city,
                country: data.country_name
            };
        } catch (error) {
            console.error('IP geolocation error:', error);
            return null;
        }
    };

    const fetchSpecializations = async () => {
        try {
            const response = await api.get('/api/search/specializations');
            setSpecializations(response.data.specializations || []);
        } catch (err) {
            console.error('Error fetching specializations:', err);
        }
    };

    const handleSearch = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            let response;
            if (useGPS && searchParams.latitude && searchParams.longitude) {
                response = await api.get('/api/search/hospitals', {
                    params: {
                        latitude: searchParams.latitude,
                        longitude: searchParams.longitude,
                        max_distance_km: searchParams.max_distance_km,
                        specialization: searchParams.specialization || undefined,
                        has_beds: searchParams.has_beds,
                        has_icu: searchParams.has_icu,
                        has_ventilator: searchParams.has_ventilator,
                        sort_by: searchParams.sort_by
                    }
                });
            } else {
                response = await api.get('/api/search/nearby-hospitals', {
                    params: { city: searchParams.city, limit: 20 }
                });
            }

            setHospitals(response.data.results || []);
            if (response.data.results?.length === 0) {
                setError('No hospitals found matching your criteria');
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Error searching hospitals');
            console.error('Search error:', err);
        } finally {
            setLoading(false);
        }
    };

    const getLoadColor = (occupancy) => {
        if (occupancy >= 95) return 'bg-red-100 text-red-800';
        if (occupancy >= 80) return 'bg-orange-100 text-orange-800';
        if (occupancy >= 60) return 'bg-yellow-100 text-yellow-800';
        return 'bg-green-100 text-green-800';
    };

    const getStatusText = (occupancy) => {
        if (occupancy >= 95) return 'Critical';
        if (occupancy >= 80) return 'High Load';
        if (occupancy >= 60) return 'Moderate';
        return 'Available';
    };

    return (
        <div className="space-y-6">
            <Card className="p-6">
                <h1 className="text-2xl font-bold text-gray-900 mb-4">Find Nearby Hospitals</h1>

                <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-start gap-3">
                        <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                        <div className="flex-1">
                            <h3 className="text-sm font-semibold text-blue-900 mb-1">How location detection works:</h3>
                            <ul className="text-sm text-blue-800 space-y-1">
                                <li>✓ <strong>Browser GPS</strong>: Most accurate, requires your permission</li>
                                <li>✓ <strong>Google API</strong>: Backup method, good accuracy</li>
                                <li>✓ <strong>IP-based</strong>: Approximate location, always works</li>
                            </ul>
                            <p className="text-xs text-blue-700 mt-2">
                                Enable "Use my location" and allow browser permissions for best results.
                            </p>
                        </div>
                    </div>
                </div>

                <div className="mb-4 space-y-3">
                    <label className="flex items-center gap-2">
                        <input
                            type="checkbox"
                            checked={useGPS}
                            onChange={(e) => {
                                setUseGPS(e.target.checked);
                                if (e.target.checked) getLocation();
                            }}
                            className="rounded"
                        />
                        <span className="text-sm font-medium">Use my location (GPS)</span>
                    </label>

                    {useGPS && searchParams.latitude && searchParams.longitude && (
                        <div className="flex items-center gap-2 text-sm text-green-600 bg-green-50 p-2 rounded">
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span>Location detected: {searchParams.latitude.toFixed(4)}, {searchParams.longitude.toFixed(4)}</span>
                        </div>
                    )}

                    {useGPS && loading && !searchParams.latitude && (
                        <div className="flex items-center gap-2 text-sm text-blue-600 bg-blue-50 p-2 rounded">
                            <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            <span>Detecting your location...</span>
                        </div>
                    )}
                </div>

                <form onSubmit={handleSearch} className="space-y-4">
                    {!useGPS && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                            <input
                                type="text"
                                value={searchParams.city}
                                onChange={(e) => setSearchParams(prev => ({ ...prev, city: e.target.value }))}
                                className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                placeholder="Enter city name"
                            />
                        </div>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Specialization</label>
                            <select
                                value={searchParams.specialization}
                                onChange={(e) => setSearchParams(prev => ({ ...prev, specialization: e.target.value }))}
                                className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            >
                                <option value="">All Specializations</option>
                                {specializations.map((spec) => (
                                    <option key={spec} value={spec}>{spec}</option>
                                ))}
                            </select>
                        </div>

                        {useGPS && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Max Distance (km)</label>
                                <input
                                    type="number"
                                    value={searchParams.max_distance_km}
                                    onChange={(e) => setSearchParams(prev => ({ ...prev, max_distance_km: e.target.value }))}
                                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    min="1"
                                    max="100"
                                />
                            </div>
                        )}

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
                            <select
                                value={searchParams.sort_by}
                                onChange={(e) => setSearchParams(prev => ({ ...prev, sort_by: e.target.value }))}
                                className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            >
                                <option value="distance">Distance</option>
                                <option value="beds">Available Beds</option>
                                <option value="rating">Rating</option>
                            </select>
                        </div>
                    </div>

                    <div className="flex flex-wrap gap-4">
                        <label className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                checked={searchParams.has_beds}
                                onChange={(e) => setSearchParams(prev => ({ ...prev, has_beds: e.target.checked }))}
                                className="rounded"
                            />
                            <span className="text-sm">Has Available Beds</span>
                        </label>
                        <label className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                checked={searchParams.has_icu}
                                onChange={(e) => setSearchParams(prev => ({ ...prev, has_icu: e.target.checked }))}
                                className="rounded"
                            />
                            <span className="text-sm">Has ICU</span>
                        </label>
                        <label className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                checked={searchParams.has_ventilator}
                                onChange={(e) => setSearchParams(prev => ({ ...prev, has_ventilator: e.target.checked }))}
                                className="rounded"
                            />
                            <span className="text-sm">Has Ventilator</span>
                        </label>
                    </div>

                    <Button type="submit" disabled={loading} className="w-full md:w-auto">
                        {loading ? 'Searching...' : 'Search Hospitals'}
                    </Button>
                </form>

                {error && (
                    <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                        <p className="text-sm text-red-700">{error}</p>
                    </div>
                )}
            </Card>

            {/* Map Section */}
            <Card className="p-0 overflow-hidden h-[400px]">
                {(searchParams.latitude && searchParams.longitude) || hospitals.length > 0 ? (
                    <MapContainer
                        center={[searchParams.latitude || 28.6139, searchParams.longitude || 77.2090]}
                        zoom={13}
                        style={{ height: '100%', width: '100%' }}
                    >
                        <TileLayer
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        />
                        <MapUpdater center={searchParams.latitude && searchParams.longitude ? [searchParams.latitude, searchParams.longitude] : null} />

                        {/* User Location */}
                        {searchParams.latitude && searchParams.longitude && (
                            <Marker position={[searchParams.latitude, searchParams.longitude]}>
                                <Popup>You are here</Popup>
                            </Marker>
                        )}

                        {/* Hospitals */}
                        {hospitals.map(hospital => (
                            hospital.location?.coordinates && (
                                <Marker
                                    key={hospital.id}
                                    position={[hospital.location.coordinates[1], hospital.location.coordinates[0]]}
                                >
                                    <Popup>
                                        <strong>{hospital.name}</strong><br />
                                        {hospital.capacity.available_beds} beds available
                                    </Popup>
                                </Marker>
                            )
                        ))}
                    </MapContainer>
                ) : (
                    <div className="h-full flex items-center justify-center bg-gray-100 text-gray-500">
                        Map will appear when location is detected
                    </div>
                )}
            </Card>

            <div className="space-y-4">
                {hospitals.length > 0 && (
                    <div className="text-sm text-gray-600">
                        Found {hospitals.length} hospital{hospitals.length !== 1 ? 's' : ''}
                    </div>
                )}

                {hospitals.map((hospital) => (
                    <Card key={hospital.id} className="p-6 hover:shadow-lg transition-shadow">
                        <div className="flex justify-between items-start mb-4">
                            <div className="flex-1">
                                <h3 className="text-xl font-semibold text-gray-900">{hospital.name}</h3>
                                <p className="text-gray-600 mt-1">{hospital.address}, {hospital.city}</p>
                                <div className="flex items-center gap-2 mt-2">
                                    {hospital.distance_km && (
                                        <span className="text-sm text-gray-500">📍 {hospital.distance_km} km away</span>
                                    )}
                                    {hospital.travel_time_minutes && (
                                        <span className="text-sm text-gray-500">• ⏱️ ~{hospital.travel_time_minutes} min</span>
                                    )}
                                </div>
                            </div>
                            <div className="text-right">
                                <span className={`px-3 py-1 text-sm font-semibold rounded-full ${getLoadColor(hospital.capacity.occupancy_percentage)}`}>
                                    {getStatusText(hospital.capacity.occupancy_percentage)}
                                </span>
                                <p className="text-xs text-gray-500 mt-1">{hospital.capacity.occupancy_percentage}% occupied</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                            <div className="bg-blue-50 p-3 rounded-lg">
                                <p className="text-xs text-gray-600">Available Beds</p>
                                <p className="text-2xl font-bold text-blue-600">{hospital.capacity.available_beds}</p>
                                <p className="text-xs text-gray-500">of {hospital.capacity.total_beds}</p>
                            </div>
                            <div className="bg-purple-50 p-3 rounded-lg">
                                <p className="text-xs text-gray-600">ICU Beds</p>
                                <p className="text-2xl font-bold text-purple-600">{hospital.capacity.icu_beds}</p>
                            </div>
                            <div className="bg-green-50 p-3 rounded-lg">
                                <p className="text-xs text-gray-600">Ventilators</p>
                                <p className="text-2xl font-bold text-green-600">{hospital.capacity.ventilators}</p>
                            </div>
                            <div className="bg-yellow-50 p-3 rounded-lg">
                                <p className="text-xs text-gray-600">Rating</p>
                                <p className="text-2xl font-bold text-yellow-600">⭐ {hospital.rating}</p>
                            </div>
                        </div>

                        <div className="mb-4">
                            <p className="text-sm font-medium text-gray-700 mb-2">Specializations:</p>
                            <div className="flex flex-wrap gap-2">
                                {hospital.specializations.map((spec, idx) => (
                                    <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                                        {spec}
                                    </span>
                                ))}
                            </div>
                        </div>

                        <div className="flex gap-3">
                            <Button
                                variant="primary"
                                onClick={() => window.open(`tel:${hospital.phone}`)}
                                className="flex-1"
                            >
                                📞 Call Now
                            </Button>
                            <Button
                                variant="outline"
                                onClick={() => setReviewHospital(hospital)}
                                className="flex-1"
                            >
                                ⭐ Review
                            </Button>
                            <Button
                                variant="primary"
                                onClick={() => setBookingHospital(hospital)}
                                className="flex-1"
                            >
                                📅 Book
                            </Button>
                            <Button
                                variant="outline"
                                onClick={() => window.location.href = `/patient/referral?hospital=${hospital.id}`}
                                className="flex-1"
                            >
                                Request Referral
                            </Button>
                        </div>
                    </Card>
                ))}
            </div>

            {hospitals.length === 0 && !loading && !error && (
                <Card className="p-12 text-center">
                    <p className="text-gray-500">Use the search form above to find hospitals near you</p>
                </Card>
            )}

            {reviewHospital && (
                <ReviewModal
                    hospitalId={reviewHospital.id}
                    hospitalName={reviewHospital.name}
                    onClose={() => setReviewHospital(null)}
                    onSuccess={() => {
                        handleSearch({ preventDefault: () => { } });
                    }}
                />
            )}

            {bookingHospital && (
                <AppointmentBooking
                    hospitalId={bookingHospital.id}
                    hospitalName={bookingHospital.name}
                    onClose={() => setBookingHospital(null)}
                    onSuccess={(appointment) => {
                        alert(`Appointment booked successfully for ${new Date(appointment.scheduled_time).toLocaleString()}`);
                    }}
                />
            )}
        </div>
    );
};

export default HospitalSearch;
