import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './IncomingCallRequests.css';

const IncomingCallRequests = ({ userId }) => {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);

    // Poll for incoming requests every 5 seconds
    useEffect(() => {
        if (!userId) return;

        const fetchIncomingRequests = async () => {
            try {
                const { data } = await axios.get(`/api/call/incoming/${userId}`);
                if (data.success) {
                    setRequests(data.requests || []);
                }
            } catch (error) {
                console.error('Error fetching incoming requests:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchIncomingRequests();
        const interval = setInterval(fetchIncomingRequests, 5000); // Poll every 5 seconds

        return () => clearInterval(interval);
    }, [userId]);

    const handleAccept = async (requestId) => {
        try {
            const { data } = await axios.post(`/api/call/accept/${requestId}`, {
                user_id: userId
            });

            if (data.success) {
                alert(`✅ Call accepted!\n\nCall will start now for ${data.call_session.duration_minutes} minutes.`);
                // Refresh to update UI
                window.location.reload();
            } else {
                alert(`❌ ${data.error || 'Failed to accept call'}`);
            }
        } catch (error) {
            console.error('Error accepting call:', error);
            alert('❌ Failed to accept call. Please try again.');
        }
    };

    const handleReject = async (requestId) => {
        try {
            const { data } = await axios.post(`/api/call/reject/${requestId}`, {
                user_id: userId
            });

            if (data.success) {
                alert('Call request rejected');
                // Remove from list
                setRequests(requests.filter(r => r.request_id !== requestId));
            } else {
                alert(`Failed to reject: ${data.error}`);
            }
        } catch (error) {
            console.error('Error rejecting call:', error);
            alert('Failed to reject call');
        }
    };

    if (loading) {
        return <div className="incoming-requests-loading">Loading requests...</div>;
    }

    if (requests.length === 0) {
        return null; // Don't show anything if no requests
    }

    return (
        <div className="incoming-requests-container">
            <h3>📞 Incoming Call Requests ({requests.length})</h3>
            <div className="requests-list">
                {requests.map((request) => (
                    <div key={request.request_id} className="call-request-card">
                        <div className="request-header">
                            <img
                                src={request.caller_info?.avatar || '/default-avatar.png'}
                                alt={request.caller_info?.name}
                                className="caller-avatar"
                            />
                            <div className="caller-info">
                                <h4>{request.caller_info?.name || 'Unknown User'}</h4>
                                <p className="caller-role">{request.caller_info?.role}</p>
                            </div>
                        </div>

                        <div className="request-details">
                            <p><strong>Duration:</strong> {request.duration_minutes} minutes</p>
                            <p><strong>Amount:</strong> ₹{request.amount}</p>
                            <p className="request-time">
                                Requested: {new Date(request.created_at).toLocaleString()}
                            </p>
                        </div>

                        <div className="request-actions">
                            <button
                                className="btn-reject"
                                onClick={() => handleReject(request.request_id)}
                            >
                                ❌ Reject
                            </button>
                            <button
                                className="btn-accept"
                                onClick={() => handleAccept(request.request_id)}
                            >
                                ✅ Accept Call
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default IncomingCallRequests;
