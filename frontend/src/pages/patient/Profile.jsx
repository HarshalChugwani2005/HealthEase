import React from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { useAuthStore } from '../../store/authStore';

const PatientProfile = () => {
    const { user } = useAuthStore();

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-900">My Profile</h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="p-6 md:col-span-1">
                    <div className="flex flex-col items-center">
                        <div className="w-32 h-32 bg-gray-200 rounded-full flex items-center justify-center text-4xl text-gray-500 mb-4">
                            {user?.full_name?.charAt(0) || 'U'}
                        </div>
                        <h2 className="text-xl font-bold text-gray-900">{user?.full_name || 'User Name'}</h2>
                        <p className="text-gray-500">{user?.email || 'email@example.com'}</p>
                        <div className="mt-6 w-full">
                            <Button className="w-full" variant="outline">Edit Profile</Button>
                        </div>
                    </div>
                </Card>

                <Card className="p-6 md:col-span-2">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Personal Information</h3>
                    <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-6">
                        <div>
                            <dt className="text-sm font-medium text-gray-500">Full Name</dt>
                            <dd className="mt-1 text-sm text-gray-900">{user?.full_name || '-'}</dd>
                        </div>
                        <div>
                            <dt className="text-sm font-medium text-gray-500">Phone Number</dt>
                            <dd className="mt-1 text-sm text-gray-900">{user?.phone_number || '-'}</dd>
                        </div>
                        <div>
                            <dt className="text-sm font-medium text-gray-500">Blood Group</dt>
                            <dd className="mt-1 text-sm text-gray-900">O+</dd>
                        </div>
                        <div>
                            <dt className="text-sm font-medium text-gray-500">Date of Birth</dt>
                            <dd className="mt-1 text-sm text-gray-900">Jan 1, 1990</dd>
                        </div>
                        <div className="sm:col-span-2">
                            <dt className="text-sm font-medium text-gray-500">Address</dt>
                            <dd className="mt-1 text-sm text-gray-900">123 Health St, Wellness City, HC 12345</dd>
                        </div>
                    </dl>
                </Card>
            </div>
        </div>
    );
};

export default PatientProfile;
