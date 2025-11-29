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
        item_name: '',
        category: 'medicine',
        current_stock: 0,
        reorder_threshold: 0,
        unit_price: 0,
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
            setNewItem({ item_name: '', category: 'medicine', current_stock: 0, reorder_threshold: 0, unit_price: 0, unit: 'units' });
            setShowAddForm(false);
            fetchInventory();
            fetchAlerts();
        } catch (err) {
            console.error('Add item error:', err);
            const errorMessage = err.response?.data?.detail || err.message || 'Error adding item';
            alert(typeof errorMessage === 'object' ? JSON.stringify(errorMessage) : errorMessage);
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
            medicine: 'bg-blue-100 text-blue-800',
            equipment: 'bg-purple-100 text-purple-800',
            consumable: 'bg-green-100 text-green-800',
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
                                • {alert.item_name}: {alert.current_stock} {alert.unit} (minimum: {alert.reorder_threshold})
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
                                    value={newItem.item_name}
                                    onChange={(e) => setNewItem({ ...newItem, item_name: e.target.value })}
                                    className="w-full rounded-md border-gray-300"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                                <select
                                    value={newItem.category}
                                    onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}
                                    className="w-full rounded-md border-gray-300"
                                >
                                    <option value="medicine">Medicine</option>
                                    <option value="equipment">Equipment</option>
                                    <option value="consumable">Consumable</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Current Stock</label>
                                <input
                                    type="number"
                                    value={newItem.current_stock}
                                    onChange={(e) => setNewItem({ ...newItem, current_stock: parseInt(e.target.value) || 0 })}
                                    className="w-full rounded-md border-gray-300"
                                    min="0"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Reorder Threshold</label>
                                <input
                                    type="number"
                                    value={newItem.reorder_threshold}
                                    onChange={(e) => setNewItem({ ...newItem, reorder_threshold: parseInt(e.target.value) || 0 })}
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
                                    onChange={(e) => setNewItem({ ...newItem, unit: e.target.value })}
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
                                        <td className="px-4 py-3 text-sm font-medium text-gray-900">{item.item_name}</td>
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
                                                    onClick={() => handleUpdateQuantity(item.id, item.current_stock - 1)}
                                                    disabled={item.current_stock <= 0}
                                                >
                                                    -
                                                </Button>
                                                <span className="text-sm font-semibold w-12 text-center">{item.current_stock}</span>
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => handleUpdateQuantity(item.id, item.current_stock + 1)}
                                                >
                                                    +
                                                </Button>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 text-sm text-gray-600">{item.reorder_threshold}</td>
                                        <td className="px-4 py-3 text-sm text-gray-600">{item.unit || 'units'}</td>
                                        <td className="px-4 py-3">
                                            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${item.current_stock <= item.reorder_threshold ? 'bg-red-100 text-red-800' :
                                                item.current_stock <= item.reorder_threshold * 2 ? 'bg-yellow-100 text-yellow-800' :
                                                    'bg-green-100 text-green-800'
                                                }`}>
                                                {item.current_stock <= item.reorder_threshold ? 'Low' :
                                                    item.current_stock <= item.reorder_threshold * 2 ? 'Medium' : 'Good'}
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
