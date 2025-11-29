import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { NotificationCenter } from '../../components/ui/NotificationCenter';
import AppointmentBooking from '../../components/ui/AppointmentBooking';
import api from '../../lib/api';

const AppointmentCard = ({ appointment, getTypeIcon, getStatusColor }) => (
    <Card className="p-6">
        <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
                <div className="text-3xl">
                    {getTypeIcon(appointment.appointment_type)}
                </div>
                <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                            {appointment.hospital_name}
                        </h3>
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(appointment.status)}`}>
                            {appointment.status.replace('_', ' ').toUpperCase()}
                        </span>
                    </div>
                    <div className="space-y-1 text-sm text-gray-600">
                        <p><strong>Specialization:</strong> {appointment.specialization}</p>
                        <p><strong>Type:</strong> {appointment.appointment_type.replace('_', ' ')}</p>
                        <p><strong>Date & Time:</strong> {new Date(appointment.scheduled_time).toLocaleString()}</p>
                    </div>
                </div>
            </div>
            <div className="flex flex-col gap-2">
                {appointment.meeting_url && appointment.status === 'confirmed' && (
                    <Button
                        variant="primary"
                        size="sm"
                        onClick={() => window.open(appointment.meeting_url, '_blank')}
                    >
                        Join Video Call
                    </Button>
                )}
                {appointment.status === 'scheduled' && (
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                            if (confirm('Are you sure you want to cancel this appointment?')) {
                                // Implement cancel API call
                                alert('Cancellation not implemented yet');
                            }
                        }}
                    >
                        Cancel
                    </Button>
                )}
            </div>
        </div>

        {appointment.doctor_notes && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-1">Doctor's Notes:</h4>
                <p className="text-blue-800 text-sm">{appointment.doctor_notes}</p>
            </div>
        )}
    </Card>
);

const AppointmentsPage = () => {
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showBooking, setShowBooking] = useState(false);

    useEffect(() => {
        fetchAppointments();
    }, []);

    const fetchAppointments = async () => {
        try {
            const response = await api.get('/api/appointments/my-appointments');
            setAppointments(response.data.appointments);
        } catch (error) {
            console.error('Error fetching appointments:', error);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'scheduled': return 'bg-blue-100 text-blue-800';
            case 'confirmed': return 'bg-green-100 text-green-800';
            case 'in_progress': return 'bg-yellow-100 text-yellow-800';
            case 'completed': return 'bg-gray-100 text-gray-800';
            case 'cancelled': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const getTypeIcon = (type) => {
        switch (type) {
            case 'telemedicine': return '💻';
            case 'in_person': return '🏥';
            case 'consultation': return '👩‍⚕️';
            case 'follow_up': return '🔄';
            default: return '📅';
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading appointments...</p>
                </div>
            </div>
        );
    }

    const upcomingAppointments = appointments
        .filter(a => new Date(a.scheduled_time) >= new Date())
        .sort((a, b) => new Date(a.scheduled_time) - new Date(b.scheduled_time));

    const pastAppointments = appointments
        .filter(a => new Date(a.scheduled_time) < new Date())
        .sort((a, b) => new Date(b.scheduled_time) - new Date(a.scheduled_time));

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center py-6">
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">My Appointments</h1>
                            <p className="text-gray-600">Manage your healthcare appointments</p>
                        </div>
                        <div className="flex items-center gap-4">
                            <NotificationCenter />
                            <Button onClick={() => setShowBooking(true)}>
                                + Book Appointment
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {appointments.length === 0 ? (
                    <Card className="p-12 text-center">
                        <div className="text-6xl mb-4">📅</div>
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No appointments yet</h3>
                        <p className="text-gray-600 mb-6">Book your first appointment to get started</p>
                        <Button onClick={() => setShowBooking(true)}>
                            Book Appointment
                        </Button>
                    </Card>
                ) : (
                    <div className="space-y-8">
                        {/* Upcoming Appointments */}
                        <div>
                            <h2 className="text-xl font-bold text-gray-900 mb-4">Upcoming Appointments</h2>
                            <div className="space-y-4">
                                {upcomingAppointments.length === 0 ? (
                                    <p className="text-gray-500 italic">No upcoming appointments.</p>
                                ) : (
                                    upcomingAppointments.map((appointment) => (
                                        <AppointmentCard
                                            key={appointment.id}
                                            appointment={appointment}
                                            getTypeIcon={getTypeIcon}
                                            getStatusColor={getStatusColor}
                                        />
                                    ))
                                )}
                            </div>
                        </div>

                        {/* Past Appointments */}
                        <div>
                            <h2 className="text-xl font-bold text-gray-900 mb-4">Past Appointments</h2>
                            <div className="space-y-4 opacity-75">
                                {pastAppointments.length === 0 ? (
                                    <p className="text-gray-500 italic">No past appointments.</p>
                                ) : (
                                    pastAppointments.map((appointment) => (
                                        <AppointmentCard
                                            key={appointment.id}
                                            appointment={appointment}
                                            getTypeIcon={getTypeIcon}
                                            getStatusColor={getStatusColor}
                                        />
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {showBooking && (
                <AppointmentBooking
                    hospitalId={null} // Will be selected in modal
                    hospitalName=""
                    onClose={() => setShowBooking(false)}
                    onSuccess={(appointment) => {
                        fetchAppointments();
                        alert('Appointment booked successfully!');
                    }}
                />
            )}
        </div>
    );
};

export default AppointmentsPage;