import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import api from '../../lib/api';

const AppointmentBooking = ({ hospitalId, hospitalName, onClose, onSuccess }) => {
    const [appointmentData, setAppointmentData] = useState({
        specialization: 'General Medicine',
        appointment_type: 'in_person',
        scheduled_time: '',
        patient_notes: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const specializations = [
        'General Medicine', 'Cardiology', 'Neurology', 'Orthopedics',
        'Pediatrics', 'Gynecology', 'Dermatology', 'ENT', 'Ophthalmology'
    ];

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await api.post('/api/appointments/', {
                hospital_id: hospitalId,
                ...appointmentData,
                scheduled_time: new Date(appointmentData.scheduled_time).toISOString()
            });

            onSuccess(response.data);
            onClose();
        } catch (err) {
            setError(err.response?.data?.detail || 'Error booking appointment');
        } finally {
            setLoading(false);
        }
    };

    // Generate time slots for next 7 days
    const generateTimeSlots = () => {
        const slots = [];
        const now = new Date();
        
        for (let day = 1; day <= 7; day++) {
            const date = new Date(now);
            date.setDate(date.getDate() + day);
            
            // Generate slots from 9 AM to 5 PM
            for (let hour = 9; hour < 17; hour++) {
                const slotTime = new Date(date);
                slotTime.setHours(hour, 0, 0, 0);
                
                slots.push({
                    value: slotTime.toISOString(),
                    label: slotTime.toLocaleString('en-US', {
                        weekday: 'short',
                        month: 'short',
                        day: 'numeric',
                        hour: 'numeric',
                        minute: '2-digit',
                        hour12: true
                    })
                });
            }
        }
        
        return slots;
    };

    if (!hospitalId) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <Card className="w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
                <div className="p-6">
                    <div className="flex justify-between items-center mb-6">
                        <div>
                            <h2 className="text-xl font-bold">Book Appointment</h2>
                            <p className="text-gray-600 text-sm">{hospitalName}</p>
                        </div>
                        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                            ✕
                        </button>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Specialization
                            </label>
                            <select
                                value={appointmentData.specialization}
                                onChange={(e) => setAppointmentData(prev => ({ ...prev, specialization: e.target.value }))}
                                className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                required
                            >
                                {specializations.map((spec) => (
                                    <option key={spec} value={spec}>{spec}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Appointment Type
                            </label>
                            <select
                                value={appointmentData.appointment_type}
                                onChange={(e) => setAppointmentData(prev => ({ ...prev, appointment_type: e.target.value }))}
                                className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                required
                            >
                                <option value="in_person">In-Person Visit</option>
                                <option value="telemedicine">Telemedicine (Video Call)</option>
                                <option value="consultation">Consultation</option>
                                <option value="follow_up">Follow-up</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Preferred Time
                            </label>
                            <select
                                value={appointmentData.scheduled_time}
                                onChange={(e) => setAppointmentData(prev => ({ ...prev, scheduled_time: e.target.value }))}
                                className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                required
                            >
                                <option value="">Select a time slot</option>
                                {generateTimeSlots().map((slot) => (
                                    <option key={slot.value} value={slot.value}>
                                        {slot.label}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Notes (Optional)
                            </label>
                            <textarea
                                value={appointmentData.patient_notes}
                                onChange={(e) => setAppointmentData(prev => ({ ...prev, patient_notes: e.target.value }))}
                                className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                rows="3"
                                placeholder="Describe your symptoms or reason for visit..."
                            />
                        </div>

                        {error && (
                            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                                <p className="text-sm text-red-700">{error}</p>
                            </div>
                        )}

                        <div className="flex justify-end gap-3 pt-4">
                            <Button type="button" variant="outline" onClick={onClose}>
                                Cancel
                            </Button>
                            <Button type="submit" disabled={loading}>
                                {loading ? 'Booking...' : 'Book Appointment'}
                            </Button>
                        </div>
                    </form>
                </div>
            </Card>
        </div>
    );
};

export default AppointmentBooking;