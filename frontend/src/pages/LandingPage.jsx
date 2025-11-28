import React from 'react';
import { Link } from 'react-router-dom';
import { Building2, Users, BarChart3, Zap, Shield, TrendingUp } from 'lucide-react';
import Button from '../components/ui/Button';

const LandingPage = () => {
    return (
        <div className="min-h-screen bg-white">
            {/* Hero Section */}
            <div className="relative overflow-hidden">
                <div className="gradient-hospital absolute inset-0 opacity-10"></div>

                <nav className="relative container mx-auto px-4 py-6">
                    <div className="flex items-center justify-between">
                        <h1 className="text-3xl font-bold text-gray-900">HealthEase</h1>
                        <div className="space-x-4">
                            <Link to="/login">
                                <Button variant="outline" size="md">
                                    Login
                                </Button>
                            </Link>
                            <Link to="/register">
                                <Button variant="primary" size="md">
                                    Get Started
                                </Button>
                            </Link>
                        </div>
                    </div>
                </nav>

                <div className="relative container mx-auto px-4 py-20 text-center">
                    <h2 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
                        AI-Powered Hospital<br />Management Platform
                    </h2>
                    <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
                        Intelligent patient flow management with real-time surge predictions,
                        smart referrals, and seamless digital payments
                    </p>
                    <div className="flex justify-center gap-4">
                        <Link to="/register">
                            <Button variant="primary" size="lg" className="px-8">
                                Start Free Trial
                            </Button>
                        </Link>
                        <Link to="#features">
                            <Button variant="outline" size="lg" className="px-8">
                                Learn More
                            </Button>
                        </Link>
                    </div>
                </div>
            </div>

            {/* Features Section */}
            <div id="features" className="container mx-auto px-4 py-20">
                <h3 className="text-3xl font-bold text-center mb-12">
                    Powerful Features for Modern Healthcare
                </h3>

                <div className="grid md:grid-cols-3 gap-8">
                    {/* Feature 1 */}
                    <div className="p-6 rounded-xl border-2 border-gray-100 hover:border-hospital-primary transition-all hover:shadow-xl">
                        <div className="w-12 h-12 bg-hospital-primary/10 rounded-lg flex items-center justify-center mb-4">
                            <Zap className="w-6 h-6 text-hospital-primary" />
                        </div>
                        <h4 className="text-xl font-bold mb-3">AI Surge Predictions</h4>
                        <p className="text-gray-600">
                            Predict patient surges using multimodal data including weather, festivals,
                            pollution, and historical trends
                        </p>
                    </div>

                    {/* Feature 2 */}
                    <div className="p-6 rounded-xl border-2 border-gray-100 hover:border-patient-primary transition-all hover:shadow-xl">
                        <div className="w-12 h-12 bg-patient-primary/10 rounded-lg flex items-center justify-center mb-4">
                            <Building2 className="w-6 h-6 text-patient-primary" />
                        </div>
                        <h4 className="text-xl font-bold mb-3">Smart Referrals</h4>
                        <p className="text-gray-600">
                            Automatically redirect patients to available hospitals with real-time
                            capacity monitoring and load probability
                        </p>
                    </div>

                    {/* Feature 3 */}
                    <div className="p-6 rounded-xl border-2 border-gray-100 hover:border-admin-accent transition-all hover:shadow-xl">
                        <div className="w-12 h-12 bg-admin-accent/10 rounded-lg flex items-center justify-center mb-4">
                            <Shield className="w-6 h-6 text-admin-accent" />
                        </div>
                        <h4 className="text-xl font-bold mb-3">Digital Wallet</h4>
                        <p className="text-gray-600">
                            Platform-managed wallet system for transparent revenue sharing
                            between hospitals
                        </p>
                    </div>

                    {/* Feature 4 */}
                    <div className="p-6 rounded-xl border-2 border-gray-100 hover:border-hospital-secondary transition-all hover:shadow-xl">
                        <div className="w-12 h-12 bg-hospital-secondary/10 rounded-lg flex items-center justify-center mb-4">
                            <Users className="w-6 h-6 text-hospital-secondary" />
                        </div>
                        <h4 className="text-xl font-bold mb-3">Inventory Management</h4>
                        <p className="text-gray-600">
                            Auto-reorder supplies during festival seasons. Get low-stock alerts
                            and manage inventory efficiently
                        </p>
                    </div>

                    {/* Feature 5 */}
                    <div className="p-6 rounded-xl border-2 border-gray-100 hover:border-patient-secondary transition-all hover:shadow-xl">
                        <div className="w-12 h-12 bg-patient-secondary/10 rounded-lg flex items-center justify-center mb-4">
                            <BarChart3 className="w-6 h-6 text-patient-secondary" />
                        </div>
                        <h4 className="text-xl font-bold mb-3">Real-time Analytics</h4>
                        <p className="text-gray-600">
                            Comprehensive dashboards with occupancy tracking, referral metrics,
                            and revenue analytics
                        </p>
                    </div>

                    {/* Feature 6 */}
                    <div className="p-6 rounded-xl border-2 border-gray-100 hover:border-green-500 transition-all hover:shadow-xl">
                        <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center mb-4">
                            <TrendingUp className="w-6 h-6 text-green-500" />
                        </div>
                        <h4 className="text-xl font-bold mb-3">n8n Automation</h4>
                        <p className="text-gray-600">
                            Automated workflows for data sync, predictions, alerts, and
                            payment distribution
                        </p>
                    </div>
                </div>
            </div>

            {/* Pricing Preview */}
            <div className="bg-gray-50 py-20">
                <div className="container mx-auto px-4">
                    <h3 className="text-3xl font-bold text-center mb-12">
                        Simple, Transparent Pricing
                    </h3>

                    <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                        {/* Free Plan */}
                        <div className="bg-white p-8 rounded-2xl shadow-lg border-2 border-gray-200">
                            <h4 className="text-2xl font-bold mb-2">Free</h4>
                            <p className="text-4xl font-bold mb-6">₹0<span className="text-lg text-gray-600">/month</span></p>
                            <ul className="space-y-3 mb-8">
                                <li className="flex items-center">
                                    <span className="text-green-500 mr-2">✓</span>
                                    Basic inventory alerts
                                </li>
                                <li className="flex items-center">
                                    <span className="text-green-500 mr-2">✓</span>
                                    Referral management
                                </li>
                                <li className="flex items-center">
                                    <span className="text-green-500 mr-2">✓</span>
                                    Digital wallet
                                </li>
                                <li className="flex items-center text-gray-400">
                                    <span className="mr-2">✗</span>
                                    AI surge predictions
                                </li>
                            </ul>
                            <Link to="/register">
                                <Button variant="outline" size="lg" className="w-full">
                                    Start Free
                                </Button>
                            </Link>
                        </div>

                        {/* Paid Plan */}
                        <div className="bg-gradient-to-br from-hospital-primary to-hospital-secondary p-8 rounded-2xl shadow-xl text-white border-2 border-hospital-primary">
                            <div className="bg-admin-accent text-white px-3 py-1 rounded-full text-sm inline-block mb-4">
                                Recommended
                            </div>
                            <h4 className="text-2xl font-bold mb-2">Pro</h4>
                            <p className="text-4xl font-bold mb-6">₹999<span className="text-lg opacity-80">/month</span></p>
                            <ul className="space-y-3 mb-8">
                                <li className="flex items-center">
                                    <span className="mr-2">✓</span>
                                    Everything in Free
                                </li>
                                <li className="flex items-center">
                                    <span className="mr-2">✓</span>
                                    AI-powered surge predictions
                                </li>
                                <li className="flex items-center">
                                    <span className="mr-2">✓</span>
                                    Auto-reorder inventory
                                </li>
                                <li className="flex items-center">
                                    <span className="mr-2">✓</span>
                                    Advanced analytics
                                </li>
                                <li className="flex items-center">
                                    <span className="mr-2">✓</span>
                                    Priority support
                                </li>
                            </ul>
                            <Link to="/register">
                                <Button variant="secondary" size="lg" className="w-full">
                                    Start Pro Trial
                                </Button>
                            </Link>
                        </div>
                    </div>
                </div>
            </div>

            {/* CTA Section */}
            <div className="container mx-auto px-4 py-20 text-center">
                <h3 className="text-4xl font-bold mb-6">
                    Ready to Transform Your Hospital?
                </h3>
                <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
                    Join hundreds of hospitals using HealthEase to optimize patient flow
                    and improve care delivery
                </p>
                <Link to="/register">
                    <Button variant="primary" size="lg" className="px-12">
                        Get Started Today
                    </Button>
                </Link>
            </div>

            {/* Footer */}
            <footer className="bg-gray-900 text-gray-400 py-12">
                <div className="container mx-auto px-4 text-center">
                    <p className="text-sm">
                        ©  2025 HealthEase. All rights reserved.
                    </p>
                    <p className="text-xs mt-2">
                        Agentic AI Hospital Management & Patient Flow Platform
                    </p>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
