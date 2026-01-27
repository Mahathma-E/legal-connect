import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

const VerifyEmail = () => {
    const { token } = useParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState('verifying'); // verifying, success, error
    const [message, setMessage] = useState('');

    useEffect(() => {
        verifyEmail();
    }, [token]);

    const verifyEmail = async () => {
        try {
            const response = await axios.get(`/api/auth/verify-email/${token}`);
            setStatus('success');
            setMessage(response.data.message || 'Email verified successfully!');

            // Redirect to login after 3 seconds
            setTimeout(() => {
                navigate('/');
            }, 3000);
        } catch (error) {
            setStatus('error');
            setMessage(error.response?.data?.error || 'Verification failed. The link may be invalid or expired.');
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card glass-card">
                <div style={{ textAlign: 'center', padding: '40px 20px' }}>
                    {status === 'verifying' && (
                        <>
                            <div className="spinner" style={{
                                border: '4px solid rgba(255,255,255,0.1)',
                                borderTop: '4px solid var(--color-primary)',
                                borderRadius: '50%',
                                width: '50px',
                                height: '50px',
                                animation: 'spin 1s linear infinite',
                                margin: '0 auto 20px'
                            }}></div>
                            <h2>Verifying Your Email...</h2>
                            <p className="muted">Please wait while we verify your email address.</p>
                        </>
                    )}

                    {status === 'success' && (
                        <>
                            <div style={{ fontSize: '60px', marginBottom: '20px' }}>✅</div>
                            <h2 style={{ color: 'var(--color-success)' }}>Email Verified!</h2>
                            <p>{message}</p>
                            <p className="muted">Redirecting to login page...</p>
                            <Link to="/" className="btn btn-primary" style={{ marginTop: '20px', display: 'inline-block' }}>
                                Go to Login
                            </Link>
                        </>
                    )}

                    {status === 'error' && (
                        <>
                            <div style={{ fontSize: '60px', marginBottom: '20px' }}>❌</div>
                            <h2 style={{ color: 'var(--color-error)' }}>Verification Failed</h2>
                            <p>{message}</p>
                            <div style={{ marginTop: '30px' }}>
                                <Link to="/" className="btn btn-secondary">
                                    Back to Login
                                </Link>
                            </div>
                        </>
                    )}
                </div>
            </div>

            <style jsx>{`
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    );
};

export default VerifyEmail;
