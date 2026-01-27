import React, { useState, useEffect } from 'react';
import './AdminCallSettings.css';

const AdminCallSettings = ({ adminId }) => {
    const [settings, setSettings] = useState(null);
    const [callHistory, setCallHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState(null);

    // Form state
    const [callPrice, setCallPrice] = useState(20);
    const [callDuration, setCallDuration] = useState(10);
    const [featureEnabled, setFeatureEnabled] = useState(true);

    useEffect(() => {
        fetchSettings();
        fetchCallHistory();
    }, []);

    const fetchSettings = async () => {
        try {
            const response = await fetch('/api/admin/call-settings');
            const data = await response.json();

            if (response.ok) {
                setSettings(data);
                setCallPrice(data.call_price);
                setCallDuration(data.call_duration);
                setFeatureEnabled(data.feature_enabled);
            }
        } catch (error) {
            console.error('Error fetching settings:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchCallHistory = async () => {
        try {
            const response = await fetch('/api/admin/call-history?limit=100');
            const data = await response.json();

            if (data.success) {
                setCallHistory(data.history);
            }
        } catch (error) {
            console.error('Error fetching call history:', error);
        }
    };

    const handleSaveSettings = async (e) => {
        e.preventDefault();
        setSaving(true);
        setMessage(null);

        try {
            const response = await fetch('/api/admin/call-settings', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    admin_id: adminId,
                    call_price: parseInt(callPrice),
                    call_duration: parseInt(callDuration),
                    feature_enabled: featureEnabled
                })
            });

            const data = await response.json();

            if (data.success) {
                setMessage({ type: 'success', text: 'Settings updated successfully!' });
                fetchSettings();
            } else {
                setMessage({ type: 'error', text: data.error || 'Failed to update settings' });
            }
        } catch (error) {
            setMessage({ type: 'error', text: 'Error updating settings' });
            console.error('Error saving settings:', error);
        } finally {
            setSaving(false);
        }
    };

    const calculateStats = () => {
        const totalCalls = callHistory.length;
        const totalRevenue = callHistory.reduce((sum, call) => sum + (call.amount || 0), 0);
        const completedCalls = callHistory.filter(call => call.status === 'completed').length;
        const activeCalls = callHistory.filter(call => call.status === 'active').length;

        return { totalCalls, totalRevenue, completedCalls, activeCalls };
    };

    if (loading) {
        return <div className="admin-call-settings">Loading...</div>;
    }

    const stats = calculateStats();

    return (
        <div className="admin-call-settings">
            <h2>⚙️ Call Feature Settings</h2>

            {/* Statistics Dashboard */}
            <div className="stats-dashboard">
                <div className="stat-box">
                    <div className="stat-icon">📞</div>
                    <div className="stat-info">
                        <div className="stat-value">{stats.totalCalls}</div>
                        <div className="stat-label">Total Calls</div>
                    </div>
                </div>

                <div className="stat-box">
                    <div className="stat-icon">💰</div>
                    <div className="stat-info">
                        <div className="stat-value">₹{stats.totalRevenue}</div>
                        <div className="stat-label">Total Revenue</div>
                    </div>
                </div>

                <div className="stat-box">
                    <div className="stat-icon">✅</div>
                    <div className="stat-info">
                        <div className="stat-value">{stats.completedCalls}</div>
                        <div className="stat-label">Completed</div>
                    </div>
                </div>

                <div className="stat-box">
                    <div className="stat-icon">🔴</div>
                    <div className="stat-info">
                        <div className="stat-value">{stats.activeCalls}</div>
                        <div className="stat-label">Active</div>
                    </div>
                </div>
            </div>

            {/* Settings Form */}
            <div className="settings-form-container">
                <h3>Configuration</h3>

                {message && (
                    <div className={`message ${message.type}`}>
                        {message.type === 'success' ? '✅' : '⚠️'} {message.text}
                    </div>
                )}

                <form onSubmit={handleSaveSettings} className="settings-form">
                    <div className="form-group">
                        <label htmlFor="callPrice">
                            Call Price (₹)
                            <span className="help-text">Amount charged per call</span>
                        </label>
                        <input
                            type="number"
                            id="callPrice"
                            value={callPrice}
                            onChange={(e) => setCallPrice(e.target.value)}
                            min="1"
                            max="1000"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="callDuration">
                            Call Duration (minutes)
                            <span className="help-text">Maximum duration per call</span>
                        </label>
                        <input
                            type="number"
                            id="callDuration"
                            value={callDuration}
                            onChange={(e) => setCallDuration(e.target.value)}
                            min="1"
                            max="60"
                            required
                        />
                    </div>

                    <div className="form-group checkbox-group">
                        <label className="checkbox-label">
                            <input
                                type="checkbox"
                                checked={featureEnabled}
                                onChange={(e) => setFeatureEnabled(e.target.checked)}
                            />
                            <span>Enable Calling Feature</span>
                        </label>
                        <span className="help-text">
                            {featureEnabled ? 'Users can make calls' : 'Calling is disabled for all users'}
                        </span>
                    </div>

                    <button
                        type="submit"
                        className="save-btn"
                        disabled={saving}
                    >
                        {saving ? 'Saving...' : 'Save Settings'}
                    </button>
                </form>
            </div>

            {/* Recent Calls */}
            <div className="recent-calls">
                <h3>Recent Calls</h3>
                {callHistory.length === 0 ? (
                    <p className="no-calls">No calls yet</p>
                ) : (
                    <div className="calls-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Caller</th>
                                    <th>Receiver</th>
                                    <th>Duration</th>
                                    <th>Amount</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {callHistory.slice(0, 10).map((call, index) => (
                                    <tr key={index}>
                                        <td>{new Date(call.started_at).toLocaleString('en-IN', {
                                            day: '2-digit',
                                            month: 'short',
                                            hour: '2-digit',
                                            minute: '2-digit'
                                        })}</td>
                                        <td>{call.caller_id}</td>
                                        <td>{call.receiver_id}</td>
                                        <td>{call.duration_minutes} min</td>
                                        <td>₹{call.amount}</td>
                                        <td>
                                            <span className={`status-badge ${call.status}`}>
                                                {call.status}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminCallSettings;
