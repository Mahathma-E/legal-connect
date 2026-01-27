import React, { useState, useEffect } from 'react';
import './CallInterface.css';

const CallInterface = ({ callSessionId, targetUserName, durationMinutes, onCallEnd }) => {
    const [timeRemaining, setTimeRemaining] = useState(durationMinutes * 60); // Convert to seconds
    const [callEnded, setCallEnded] = useState(false);

    useEffect(() => {
        // Countdown timer
        const timer = setInterval(() => {
            setTimeRemaining((prev) => {
                if (prev <= 1) {
                    handleEndCall(true); // Auto-end when time runs out
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(timer);
    }, []);

    const handleEndCall = async (autoEnd = false) => {
        if (callEnded) return;

        try {
            setCallEnded(true);

            const response = await fetch('/api/call/end', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    call_session_id: callSessionId
                })
            });

            const data = await response.json();

            if (data.success) {
                const message = autoEnd
                    ? `Call ended automatically after ${durationMinutes} minutes`
                    : `Call ended. Duration: ${data.actual_duration_minutes.toFixed(2)} minutes`;

                alert(message);
                onCallEnd();
            }
        } catch (error) {
            console.error('Error ending call:', error);
            alert('Error ending call. Please try again.');
            setCallEnded(false);
        }
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    const progressPercentage = (timeRemaining / (durationMinutes * 60)) * 100;

    return (
        <div className="call-interface-overlay">
            <div className="call-interface">
                <div className="call-header">
                    <h3>📞 Calling</h3>
                    <p className="caller-name">{targetUserName}</p>
                </div>

                <div className="call-timer">
                    <div className="timer-display">
                        ⏱️ {formatTime(timeRemaining)}
                    </div>
                    <div className="timer-label">remaining</div>
                </div>

                <div className="call-progress">
                    <div
                        className="progress-bar"
                        style={{ width: `${progressPercentage}%` }}
                    />
                </div>

                <div className="call-controls">
                    <button
                        className="end-call-btn"
                        onClick={() => handleEndCall(false)}
                        disabled={callEnded}
                    >
                        {callEnded ? 'Ending...' : 'End Call'}
                    </button>
                </div>

                <div className="call-info">
                    <p>💰 This call costs ₹{20} for {durationMinutes} minutes</p>
                </div>
            </div>
        </div>
    );
};

export default CallInterface;
