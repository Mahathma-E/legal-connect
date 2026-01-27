import React, { useState, useEffect } from 'react';
import './CallButton.css';

const CallButton = ({ currentUserId, targetUserId, targetUserName, targetUserRole }) => {
    const [isEligible, setIsEligible] = useState(false);
    const [eligibilityData, setEligibilityData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showPaymentModal, setShowPaymentModal] = useState(false);

    // Check eligibility on component mount
    useEffect(() => {
        checkEligibility();
    }, [currentUserId, targetUserId]);

    const checkEligibility = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/call/check-eligibility', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    caller_id: currentUserId,
                    receiver_id: targetUserId
                })
            });

            const data = await response.json();

            if (data.eligible) {
                setIsEligible(true);
                setEligibilityData(data);
            } else {
                setIsEligible(false);
                setEligibilityData(data);
            }
        } catch (error) {
            console.error('Error checking eligibility:', error);
            setIsEligible(false);
        } finally {
            setLoading(false);
        }
    };

    const handleCallClick = () => {
        if (isEligible) {
            setShowPaymentModal(true);
        }
    };

    const handleCloseModal = () => {
        setShowPaymentModal(false);
    };

    // Don't show button if checking eligibility or if target is not an Advocate
    if (loading) {
        return <button className="call-button loading" disabled>Checking...</button>;
    }

    // Only show call button for Advocate users
    if (targetUserRole !== 'Advocate') {
        return null;
    }

    return (
        <>
            <button
                className={`call-button ${isEligible ? 'enabled' : 'disabled'}`}
                onClick={handleCallClick}
                disabled={!isEligible}
                title={isEligible ? 'Start a call' : eligibilityData?.reason || 'Call not available'}
            >
                📞 Call
            </button>

            {!isEligible && eligibilityData?.reason && (
                <div className="call-info-tooltip">
                    {eligibilityData.reason}
                </div>
            )}

            {showPaymentModal && (
                <PaymentModal
                    targetUserName={targetUserName}
                    callPrice={eligibilityData.call_price}
                    callDuration={eligibilityData.call_duration}
                    walletBalance={eligibilityData.wallet_balance}
                    onClose={handleCloseModal}
                    onConfirm={() => {
                        handleCloseModal();
                    }}
                    callerId={currentUserId}
                    receiverId={targetUserId}
                />
            )}
        </>
    );
};

// Payment Modal Component
const PaymentModal = ({
    targetUserName,
    callPrice,
    callDuration,
    walletBalance,
    onClose,
    onConfirm,
    callerId,
    receiverId
}) => {
    const [processing, setProcessing] = useState(false);
    const [error, setError] = useState(null);

    const handleConfirmPayment = async () => {
        try {
            setProcessing(true);
            setError(null);

            // Step 1: Process mock payment (always succeeds)
            const paymentResponse = await fetch('/api/payment/mock', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: callerId,
                    amount: callPrice,
                    purpose: 'call_payment'
                })
            });

            const paymentData = await paymentResponse.json();

            if (!paymentResponse.ok || !paymentData.success) {
                setError('Payment processing failed. Please try again.');
                return;
            }

            // Step 2: Create call request
            const callResponse = await fetch('/api/call/request', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    caller_id: callerId,
                    receiver_id: receiverId
                })
            });

            const callData = await callResponse.json();

            if (callResponse.ok && callData.success) {
                // Call request sent successfully
                alert(`✅ Call request sent to ${targetUserName}!\n\nRequest ID: ${callData.request_id}\nStatus: Pending\n\nWaiting for ${targetUserName} to accept your call...`);
                onConfirm();
                // Reload to show updated state
                setTimeout(() => window.location.reload(), 1500);
            } else {
                setError(callData.error || 'Failed to send call request');
            }
        } catch (err) {
            setError('Network error. Please check your connection.');
            console.error('Payment/Call error:', err);
        } finally {
            setProcessing(false);
        }
    };

    const newBalance = walletBalance - callPrice;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="payment-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h3>Confirm Call Payment</h3>
                    <button className="close-btn" onClick={onClose}>×</button>
                </div>

                <div className="modal-body">
                    <div className="call-details">
                        <p><strong>Calling:</strong> {targetUserName}</p>
                        <p><strong>Duration:</strong> {callDuration} minutes</p>
                        <p><strong>Price:</strong> ₹{callPrice}</p>
                    </div>

                    <div className="wallet-info">
                        <p><strong>Your Balance:</strong> ₹{walletBalance}</p>
                        <p><strong>After Call:</strong> ₹{newBalance}</p>
                    </div>

                    {error && (
                        <div className="error-message">
                            ⚠️ {error}
                        </div>
                    )}
                </div>

                <div className="modal-footer">
                    <button
                        className="btn-cancel"
                        onClick={onClose}
                        disabled={processing}
                    >
                        Cancel
                    </button>
                    <button
                        className="btn-confirm"
                        onClick={handleConfirmPayment}
                        disabled={processing}
                    >
                        {processing ? 'Processing...' : 'Confirm & Pay'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CallButton;
