import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { sendPasswordResetEmail } from 'firebase/auth';
import { auth } from '../firebase';

const ForgotPassword = () => {
    const [email, setEmail] = useState('');
    const [status, setStatus] = useState(''); // success, error
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!email) {
            setStatus('error');
            setMessage('Please enter your email address');
            return;
        }

        setLoading(true);
        setStatus('');
        setMessage('');

        try {
            await sendPasswordResetEmail(auth, email);
            setStatus('success');
            setMessage('Password reset link sent! Please check your email.');
            setEmail('');
        } catch (error) {
            console.error(error);
            setStatus('error');
            if (error.code === 'auth/user-not-found') {
                setMessage('No account found with this email.');
            } else {
                setMessage('Failed to send reset email. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card glass-card">
                <h2 style={{ textAlign: 'center', marginBottom: '10px' }}>Forgot Password?</h2>
                <p className="muted" style={{ textAlign: 'center', marginBottom: '30px' }}>
                    Enter your email address and we'll send you a link to reset your password.
                </p>

                {status === 'success' && (
                    <div className="alert alert-success" style={{
                        padding: '15px',
                        marginBottom: '20px',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        border: '1px solid rgba(76, 175, 80, 0.3)',
                        borderRadius: '8px',
                        color: 'var(--color-success)'
                    }}>
                        <strong>✅ {message}</strong>
                        <p style={{ marginTop: '10px', fontSize: '14px' }}>
                            Check your inbox and click the reset link. The link will expire in 24 hours.
                        </p>
                    </div>
                )}

                {status === 'error' && (
                    <div className="alert alert-error" style={{
                        padding: '15px',
                        marginBottom: '20px',
                        backgroundColor: 'rgba(244, 67, 54, 0.1)',
                        border: '1px solid rgba(244, 67, 54, 0.3)',
                        borderRadius: '8px',
                        color: 'var(--color-error)'
                    }}>
                        ❌ {message}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Email Address</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Enter your email"
                            required
                            disabled={loading}
                        />
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%' }}>
                        {loading ? 'Sending...' : 'Send Reset Link'}
                    </button>
                </form>

                <div style={{ textAlign: 'center', marginTop: '20px' }}>
                    <Link to="/" style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>
                        ← Back to Login
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default ForgotPassword;
