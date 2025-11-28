import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';

const Register = () => {
    const navigate = useNavigate();
    const { register, isLoading, error } = useAuthStore();
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        full_name: '',
        role: 'patient', // Default role
        phone_number: '',
        // Hospital specific fields
        hospital_name: '',
        address: '',
        city: '',
        state: '',
        pincode: ''
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const { email, password, role, full_name, phone_number, hospital_name, address, city, state, pincode } = formData;
        
        let profile_data = {};
        if (role === 'patient') {
            profile_data = { 
                full_name, 
                phone: phone_number 
            };
        } else if (role === 'hospital') {
            profile_data = {
                name: hospital_name,
                phone: phone_number,
                address,
                city,
                state,
                pincode,
                location: { type: "Point", coordinates: [0, 0] }, // Default location
                specializations: []
            };
        }
        
        const result = await register(email, password, role, profile_data);
        if (result.success) {
            navigate('/login');
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <Card className="max-w-md w-full space-y-8 p-8">
                <div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Create your account
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        Or{' '}
                        <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
                            sign in to your existing account
                        </Link>
                    </p>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="rounded-md shadow-sm space-y-4">
                        <div>
                            <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-2">
                                Register as
                            </label>
                            <select
                                id="role"
                                name="role"
                                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                value={formData.role}
                                onChange={handleChange}
                            >
                                <option value="patient">Patient</option>
                                <option value="hospital">Hospital</option>
                            </select>
                        </div>

                        {formData.role === 'patient' ? (
                            <>
                                <div>
                                    <label htmlFor="full_name" className="sr-only">Full Name</label>
                                    <input
                                        id="full_name"
                                        name="full_name"
                                        type="text"
                                        required
                                        className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                        placeholder="Full Name"
                                        value={formData.full_name}
                                        onChange={handleChange}
                                    />
                                </div>
                            </>
                        ) : (
                            <>
                                <div>
                                    <label htmlFor="hospital_name" className="sr-only">Hospital Name</label>
                                    <input
                                        id="hospital_name"
                                        name="hospital_name"
                                        type="text"
                                        required
                                        className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                        placeholder="Hospital Name"
                                        value={formData.hospital_name}
                                        onChange={handleChange}
                                    />
                                </div>
                                <div>
                                    <label htmlFor="address" className="sr-only">Address</label>
                                    <input
                                        id="address"
                                        name="address"
                                        type="text"
                                        required
                                        className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                        placeholder="Address"
                                        value={formData.address}
                                        onChange={handleChange}
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label htmlFor="city" className="sr-only">City</label>
                                        <input
                                            id="city"
                                            name="city"
                                            type="text"
                                            required
                                            className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                            placeholder="City"
                                            value={formData.city}
                                            onChange={handleChange}
                                        />
                                    </div>
                                    <div>
                                        <label htmlFor="state" className="sr-only">State</label>
                                        <input
                                            id="state"
                                            name="state"
                                            type="text"
                                            required
                                            className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                            placeholder="State"
                                            value={formData.state}
                                            onChange={handleChange}
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label htmlFor="pincode" className="sr-only">Pincode</label>
                                    <input
                                        id="pincode"
                                        name="pincode"
                                        type="text"
                                        required
                                        className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                        placeholder="Pincode"
                                        value={formData.pincode}
                                        onChange={handleChange}
                                    />
                                </div>
                            </>
                        )}

                        <div>
                            <label htmlFor="email-address" className="sr-only">Email address</label>
                            <input
                                id="email-address"
                                name="email"
                                type="email"
                                autoComplete="email"
                                required
                                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                placeholder="Email address"
                                value={formData.email}
                                onChange={handleChange}
                            />
                        </div>
                        <div>
                            <label htmlFor="phone_number" className="sr-only">Phone Number</label>
                            <input
                                id="phone_number"
                                name="phone_number"
                                type="tel"
                                required
                                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                placeholder="Phone Number"
                                value={formData.phone_number}
                                onChange={handleChange}
                            />
                        </div>
                        <div>
                            <label htmlFor="password" className="sr-only">Password</label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                autoComplete="new-password"
                                required
                                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                placeholder="Password (min 8 chars, uppercase, lowercase, digit)"
                                value={formData.password}
                                onChange={handleChange}
                            />
                        </div>
                    </div>

                    {error && (
                        <div className="text-red-500 text-sm text-center">
                            {error}
                        </div>
                    )}

                    <div>
                        <Button
                            type="submit"
                            className="w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            isLoading={isLoading}
                        >
                            Register
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default Register;
