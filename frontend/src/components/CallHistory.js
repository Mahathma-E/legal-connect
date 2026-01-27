import React, { useState, useEffect } from 'react';
import './CallHistory.css';

const CallHistory = ({ userId }) => {
    const [callHistory, setCallHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchCallHistory();
    }, [userId]);

    const fetchCallHistory = async () => {
        try {
            setLoading(true);
            const response = await fetch(`/api/call/history/${userId}?limit=50`);
            const data = await response.json();

            if (data.success) {
                setCallHistory(data.history);
            } else {
                setError('Failed to load call history');
            }
        } catch (err) {
            setError('Error loading call history');
            console.error('Error fetching call history:', err);
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (isoString) => {
        const date = new Date(isoString);
        return date.toLocaleString('en-IN', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const calculateDuration = (startedAt, endedAt) => {
        if (!endedAt) return 'Ongoing';

        const start = new Date(startedAt);
        const end = new Date(endedAt);
        const durationMs = end - start;
        const minutes = Math.floor(durationMs / 60000);
        const seconds = Math.floor((durationMs % 60000) / 1000);

        return `${minutes}m ${seconds}s`;
    };

    if (loading) {
        return (
            <div className="call-history-container">
                <h2>📞 Call History</h2>
                <div className="loading-state">Loading call history...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="call-history-container">
                <h2>📞 Call History</h2>
                <div className="error-state">⚠️ {error}</div>
            </div>
        );
    }

    if (callHistory.length === 0) {
        return (
            <div className="call-history-container">
                <h2>📞 Call History</h2>
                <div className="empty-state">
                    <p>No call history yet</p>
                    <p className="empty-hint">Your call history will appear here</p>
                </div>
            </div>
        );
    }

    return (
        <div className="call-history-container">
            <h2>📞 Call History</h2>

            <div className="call-stats">
                <div className="stat-card">
                    <div className="stat-value">{callHistory.length}</div>
                    <div className="stat-label">Total Calls</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">
                        ₹{callHistory.reduce((sum, call) => sum + (call.amount || 0), 0)}
                    </div>
                    <div className="stat-label">Total Spent</div>
                </div>
            </div>

            <div className="call-list">
                {callHistory.map((call, index) => (
                    <div key={index} className={`call-item ${call.status}`}>
                        <div className="call-item-header">
                            <div className="call-direction">
                                {call.caller_id === userId ? (
                                    <span className="outgoing">📤 Outgoing</span>
                                ) : (
                                    <span className="incoming">📥 Incoming</span>
                                )}
                            </div>
                            <div className={`call-status status-${call.status}`}>
                                {call.status}
                            </div>
                        </div>

                        <div className="call-item-body">
                            <div className="call-detail">
                                <span className="label">Date:</span>
                                <span className="value">{formatDate(call.started_at)}</span>
                            </div>
                            <div className="call-detail">
                                <span className="label">Duration:</span>
                                <span className="value">
                                    {calculateDuration(call.started_at, call.ended_at)}
                                </span>
                            </div>
                            <div className="call-detail">
                                <span className="label">Amount:</span>
                                <span className="value amount">₹{call.amount}</span>
                            </div>
                            {call.payment_status && (
                                <div className="call-detail">
                                    <span className="label">Payment:</span>
                                    <span className={`value payment-${call.payment_status}`}>
                                        {call.payment_status}
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CallHistory;
