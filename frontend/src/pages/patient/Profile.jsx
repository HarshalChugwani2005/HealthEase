import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { useAuthStore } from '../../store/authStore';
import EditProfileModal from '../../components/ui/EditProfileModal';

const PatientProfile = () => {
    const { user } = useAuthStore();
    const profile = user?.profile || {};
    const [showEditModal, setShowEditModal] = useState(false);

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-900">My Profile</h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="p-6 md:col-span-1">
                    <div className="flex flex-col items-center">
                        <div className="w-32 h-32 bg-blue-100 rounded-full flex items-center justify-center text-4xl text-blue-600 mb-4 font-bold">
                            {profile.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                        </div>
                        <h2 className="text-xl font-bold text-gray-900">{profile.full_name || 'User Name'}</h2>
                        <p className="text-gray-500">{user?.email || 'email@example.com'}</p>
                        <div className="mt-6 w-full">
                            <Button
                                className="w-full"
                                variant="outline"
                                onClick={() => setShowEditModal(true)}
                            >
                                Edit Profile
                            </Button>
                        </div>
                    </div>
                </Card>

                <Card className="p-6 md:col-span-2">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Personal Information</h3>
                    <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-6">
                        <div>
                            <dt className="text-sm font-medium text-gray-500">Full Name</dt>
                            <dd className="mt-1 text-sm text-gray-900">{profile.full_name || '-'}</dd>
                        </div>
                        <div>
                            <dt className="text-sm font-medium text-gray-500">Phone Number</dt>
                            <dd className="mt-1 text-sm text-gray-900">{profile.phone || '-'}</dd>
                        </div>
                        <div>
                            <dt className="text-sm font-medium text-gray-500">Blood Group</dt>
                            <dd className="mt-1 text-sm text-gray-900">{profile.blood_group || '-'}</dd>
                        </div>
                        <div>
                            <dt className="text-sm font-medium text-gray-500">Date of Birth</dt>
                            <dd className="mt-1 text-sm text-gray-900">{profile.date_of_birth ? new Date(profile.date_of_birth).toLocaleDateString() : '-'}</dd>
                        </div>
                        <div className="sm:col-span-2">
                            <dt className="text-sm font-medium text-gray-500">Address</dt>
                            <dd className="mt-1 text-sm text-gray-900">
                                {[profile.address, profile.city, profile.state].filter(Boolean).join(', ') || '-'}
                            </dd>
                        </div>
                    </dl>
                </Card>
            </div>

            {showEditModal && (
                <EditProfileModal
                    profile={profile}
                    onClose={() => setShowEditModal(false)}
                    onSuccess={() => {
                        // Ideally trigger a re-fetch or just close as the store is updated
                        setShowEditModal(false);
                    }}
                />
            )}
        </div>
    );
};

export default PatientProfile;
