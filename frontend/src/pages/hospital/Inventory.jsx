import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import api from '../../lib/api';

const Inventory = () => {
    const [items, setItems] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [showAddForm, setShowAddForm] = useState(false);
    const [loading, setLoading] = useState(true);
    const [newItem, setNewItem] = useState({
        name: '',
        category: 'medicines',
        quantity: 0,
        minimum_quantity: 0,
        unit: 'units'
    });

    useEffect(() => {
        fetchInventory();
        fetchAlerts();
    }, []);

    const fetchInventory = async () => {
        try {
            const response = await api.get('/api/inventory/list');
            setItems(response.data.items || []);
        } catch (err) {
            console.error('Inventory error:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchAlerts = async () => {
        try {
            const response = await api.get('/api/inventory/alerts');
            setAlerts(response.data.low_stock_items || []);
        } catch (err) {
            console.error('Alerts error:', err);
        }
    };

    const handleAddItem = async (e) => {
        e.preventDefault();
        try {
            await api.post('/api/inventory/add', newItem);
            setNewItem({ name: '', category: 'medicines', quantity: 0, minimum_quantity: 0, unit: 'units' });
            setShowAddForm(false);
            fetchInventory();
            fetchAlerts();
        } catch (err) {
            alert(err.response?.data?.detail || 'Error adding item');
        }
    };

    const handleUpdateQuantity = async (itemId, newQuantity) => {
        try {
            await api.put(`/api/inventory/update/${itemId}`, { quantity: newQuantity });
            fetchInventory();
            fetchAlerts();
        } catch (err) {
            alert('Error updating quantity');
        }
    };

    const handleDeleteItem = async (itemId) => {
        if (!confirm('Are you sure you want to delete this item?')) return;
        try {
            await api.delete(`/api/inventory/${itemId}`);
            fetchInventory();
            fetchAlerts();
        } catch (err) {
            alert('Error deleting item');
        }
    };

    const getCategoryColor = (category) => {
        const colors = {
            medicines: 'bg-blue-100 text-blue-800',
            equipment: 'bg-purple-100 text-purple-800',
            supplies: 'bg-green-100 text-green-800',
            ppe: 'bg-yellow-100 text-yellow-800',
            blood: 'bg-red-100 text-red-800'
        };
        return colors[category] || 'bg-gray-100 text-gray-800';
    };

    if (loading) {
        return (
            <div className="space-y-6">
                <h1 className="text-2xl font-bold text-gray-900">Inventory Management</h1>
                <Card className="p-6"><p className="text-gray-600">Loading...</p></Card>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-900">Inventory Management</h1>
                <Button onClick={() => setShowAddForm(!showAddForm)}>
                    {showAddForm ? 'Cancel' : '+ Add Item'}
                </Button>
            </div>

            {alerts.length > 0 && (
                <Card className="p-4 bg-red-50 border-red-200">
                    <h3 className="text-red-800 font-semibold mb-2">⚠️ Low Stock Alerts</h3>
                    <div className="space-y-1">
                        {alerts.map((alert, idx) => (
                            <p key={idx} className="text-sm text-red-700">
                                • {alert.name}: {alert.quantity} {alert.unit} (minimum: {alert.minimum_quantity})
                            </p>
                        ))}
                    </div>
                </Card>
            )}

            {showAddForm && (
                <Card className="p-6">
                    <h2 className="text-lg font-semibold mb-4">Add New Item</h2>
                    <form onSubmit={handleAddItem} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Item Name</label>
                                <input
                                    type="text"
                                    value={newItem.name}
                                    onChange={(e) => setNewItem({...newItem, name: e.target.value})}
                                    className="w-full rounded-md border-gray-300"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                                <select
                                    value={newItem.category}
                                    onChange={(e) => setNewItem({...newItem, category: e.target.value})}
                                    className="w-full rounded-md border-gray-300"
                                >
                                    <option value="medicines">Medicines</option>
                                    <option value="equipment">Equipment</option>
                                    <option value="supplies">Supplies</option>
                                    <option value="ppe">PPE</option>
                                    <option value="blood">Blood</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
                                <input
                                    type="number"
                                    value={newItem.quantity}
                                    onChange={(e) => setNewItem({...newItem, quantity: parseInt(e.target.value) || 0})}
                                    className="w-full rounded-md border-gray-300"
                                    min="0"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Minimum Quantity</label>
                                <input
                                    type="number"
                                    value={newItem.minimum_quantity}
                                    onChange={(e) => setNewItem({...newItem, minimum_quantity: parseInt(e.target.value) || 0})}
                                    className="w-full rounded-md border-gray-300"
                                    min="0"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Unit</label>
                                <input
                                    type="text"
                                    value={newItem.unit}
                                    onChange={(e) => setNewItem({...newItem, unit: e.target.value})}
                                    className="w-full rounded-md border-gray-300"
                                    placeholder="e.g., units, boxes, liters"
                                    required
                                />
                            </div>
                        </div>

                        <Button type="submit" className="w-full">Add Item</Button>
                    </form>
                </Card>
            )}

            <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Inventory Items ({items.length})</h2>
                
                {items.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">No items in inventory. Add your first item above.</p>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Min. Qty</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unit</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {items.map((item) => (
                                    <tr key={item.id}>
                                        <td className="px-4 py-3 text-sm font-medium text-gray-900">{item.name}</td>
                                        <td className="px-4 py-3">
                                            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getCategoryColor(item.category)}`}>
                                                {item.category}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex items-center gap-2">
                                                <Button 
                                                    variant="outline" 
                                                    size="sm"
                                                    onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                                                    disabled={item.quantity <= 0}
                                                >
                                                    -
                                                </Button>
                                                <span className="text-sm font-semibold w-12 text-center">{item.quantity}</span>
                                                <Button 
                                                    variant="outline" 
                                                    size="sm"
                                                    onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                                                >
                                                    +
                                                </Button>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 text-sm text-gray-600">{item.minimum_quantity}</td>
                                        <td className="px-4 py-3 text-sm text-gray-600">{item.unit}</td>
                                        <td className="px-4 py-3">
                                            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                                                item.quantity <= item.minimum_quantity ? 'bg-red-100 text-red-800' :
                                                item.quantity <= item.minimum_quantity * 2 ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-green-100 text-green-800'
                                            }`}>
                                                {item.quantity <= item.minimum_quantity ? 'Low' :
                                                 item.quantity <= item.minimum_quantity * 2 ? 'Medium' : 'Good'}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <Button 
                                                variant="outline" 
                                                size="sm"
                                                onClick={() => handleDeleteItem(item.id)}
                                                className="text-red-600 hover:bg-red-50"
                                            >
                                                Delete
                                            </Button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </Card>
        </div>
    );
};

export default Inventory;
