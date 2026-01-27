import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

const ResetPassword = () => {
    const { token } = useParams();
    const navigate = useNavigate();
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [status, setStatus] = useState(''); // success, error
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validation
        if (!password || !confirmPassword) {
            setStatus('error');
            setMessage('Please fill in all fields');
            return;
        }

        if (password.length < 6) {
            setStatus('error');
            setMessage('Password must be at least 6 characters long');
            return;
        }

        if (password !== confirmPassword) {
            setStatus('error');
            setMessage('Passwords do not match');
            return;
        }

        setLoading(true);
        setStatus('');
        setMessage('');

        try {
            const response = await axios.post('/api/auth/reset-password', {
                token,
                password
            });

            setStatus('success');
            setMessage(response.data.message || 'Password reset successfully!');

            // Redirect to login after 3 seconds
            setTimeout(() => {
                navigate('/');
            }, 3000);
        } catch (error) {
            setStatus('error');
            setMessage(error.response?.data?.error || 'Failed to reset password. The link may be invalid or expired.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card glass-card">
                <h2 style={{ textAlign: 'center', marginBottom: '10px' }}>Reset Password</h2>
                <p className="muted" style={{ textAlign: 'center', marginBottom: '30px' }}>
                    Enter your new password below.
                </p>

                {status === 'success' && (
                    <div className="alert alert-success" style={{
                        padding: '15px',
                        marginBottom: '20px',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        border: '1px solid rgba(76, 175, 80, 0.3)',
                        borderRadius: '8px',
                        color: 'var(--color-success)',
                        textAlign: 'center'
                    }}>
                        <strong>✅ {message}</strong>
                        <p style={{ marginTop: '10px', fontSize: '14px' }}>
                            Redirecting to login page...
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
                        <label>New Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter new password (min 6 characters)"
                            required
                            disabled={loading || status === 'success'}
                        />
                    </div>

                    <div className="form-group">
                        <label>Confirm Password</label>
                        <input
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            placeholder="Confirm new password"
                            required
                            disabled={loading || status === 'success'}
                        />
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={loading || status === 'success'}
                        style={{ width: '100%' }}
                    >
                        {loading ? 'Resetting...' : 'Reset Password'}
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

export default ResetPassword;
