import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { signInWithPopup, createUserWithEmailAndPassword, sendEmailVerification } from 'firebase/auth'; // Import email auth functions
import { auth, googleProvider } from '../firebase';
import axios from 'axios';
import { FaGoogle, FaUser, FaGavel, FaEnvelope } from 'react-icons/fa';

/**
 * Register Component
 * Flow:
 * 1. Select Role (Public vs Lawyer)
 * 2. Auth Method (Google vs Email)
 * 3. Fill Details (Name, Bar ID, Password if Email)
 */
const Register = ({ setUser }) => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [role, setRole] = useState(null); // 'public' | 'lawyer'
    const [authMethod, setAuthMethod] = useState(null); // 'google' | 'email'
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false); // For email verification success state

    // Form Data
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '', // New password field
        firebaseUid: '',
        photoUrl: '',
        barCouncilId: ''
    });

    // --- STEP 1: ROLE SELECTION ---
    const handleRoleSelect = (selectedRole) => {
        setRole(selectedRole);
        setStep(2);
    };

    // --- STEP 2: AUTH METHOD SELECTION ---
    const selectEmailAuth = () => {
        setAuthMethod('email');
        setStep(3);
    };

    // --- GOOGLE AUTH HANDLER ---
    const handleGoogleSignIn = async () => {
        setAuthMethod('google');
        setLoading(true);
        setError('');
        try {
            const result = await signInWithPopup(auth, googleProvider);
            const user = result.user;

            setFormData(prev => ({
                ...prev,
                name: user.displayName || '',
                email: user.email,
                firebaseUid: user.uid,
                photoUrl: user.photoURL
            }));

            setStep(3);
        } catch (err) {
            console.error(err);
            setError('Google Sign In failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    // --- SUBMIT HANDLER (Handles both Google Finalize & Email Create) ---
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            let userUid = formData.firebaseUid;
            let userEmail = formData.email;

            // Scenario A: Email Registration (Create Firebase Account)
            if (authMethod === 'email') {
                try {
                    const userCredential = await createUserWithEmailAndPassword(auth, formData.email, formData.password);
                    const user = userCredential.user;
                    userUid = user.uid;
                    userEmail = user.email;

                    // Send Verification Email
                    await sendEmailVerification(user);
                } catch (firebaseErr) {
                    if (firebaseErr.code === 'auth/email-already-in-use') {
                        throw new Error('Email already in use. Please login.');
                    } else if (firebaseErr.code === 'auth/weak-password') {
                        throw new Error('Password is too weak.');
                    } else {
                        throw firebaseErr;
                    }
                }
            }

            // Scenario B: Backend Registration (Both Google & Created Email User)
            const payload = {
                name: formData.name,
                email: userEmail,
                firebaseUid: userUid,
                role: role,
                ...(role === 'lawyer' && { bar_code: formData.barCouncilId })
            };

            const res = await axios.post('/register', payload);

            if (authMethod === 'email') {
                // Show Success Screen for Email Verification
                setSuccess(true);
            } else {
                // Google User - Log them in directly
                if (res.data && res.data.user) {
                    setUser(res.data.user);
                    navigate('/home');
                } else {
                    navigate('/login');
                }
            }

        } catch (err) {
            console.error(err);
            setError(err.message || err.response?.data?.error || 'Registration failed.');
        } finally {
            setLoading(false);
        }
    };

    // --- SUCCESS VIEW (Email Verification) ---
    if (success) {
        return (
            <div className="auth-container">
                <div className="glass-card auth-box">
                    <div style={{ textAlign: 'center', padding: '20px' }}>
                        <div style={{ fontSize: '50px', marginBottom: '20px' }}>✅</div>
                        <h2 style={{ color: 'var(--color-success)', marginBottom: '15px' }}>Registration Successful!</h2>
                        <p style={{ marginBottom: '20px' }}>
                            We've sent a verification email to <strong>{formData.email}</strong>.
                        </p>
                        <div style={{ background: 'rgba(255,255,255,0.05)', padding: '15px', borderRadius: '8px', fontSize: '0.9rem', marginBottom: '20px' }}>
                            Please check your inbox, click the link to verify, and then log in.
                        </div>
                        <Link to="/login" className="btn primary">Go to Login</Link>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="auth-container">
            <div className="glass-card auth-box">

                {/* HEADERS */}
                <h2 style={{ textAlign: 'center', marginBottom: '10px' }}>Create Account</h2>
                <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', marginBottom: '20px' }}>
                    <div className={`step-dot ${step >= 1 ? 'active' : ''}`} style={{ background: step >= 1 ? 'var(--color-primary)' : '#ccc', width: '10px', height: '10px', borderRadius: '50%' }}></div>
                    <div className={`step-dot ${step >= 2 ? 'active' : ''}`} style={{ background: step >= 2 ? 'var(--color-primary)' : '#ccc', width: '10px', height: '10px', borderRadius: '50%' }}></div>
                    <div className={`step-dot ${step >= 3 ? 'active' : ''}`} style={{ background: step >= 3 ? 'var(--color-primary)' : '#ccc', width: '10px', height: '10px', borderRadius: '50%' }}></div>
                </div>

                {error && <div className="alert error" style={{ color: 'red', textAlign: 'center', marginBottom: '15px', background: 'rgba(255,0,0,0.1)', padding: '10px', borderRadius: '5px' }}>{error}</div>}

                {/* STEP 1: ROLE SELECT */}
                {step === 1 && (
                    <div className="fade-in">
                        <p style={{ textAlign: 'center', marginBottom: '20px' }}>Choose your account type</p>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                            <button
                                className="glass-card"
                                onClick={() => handleRoleSelect('public')}
                                style={{
                                    display: 'flex', alignItems: 'center', gap: '15px', padding: '20px',
                                    cursor: 'pointer', border: '1px solid rgba(255,255,255,0.1)',
                                    background: 'rgba(255,255,255,0.05)', textAlign: 'left'
                                }}
                            >
                                <div style={{ background: 'var(--color-primary)', padding: '10px', borderRadius: '50%' }}>
                                    <FaUser color="white" />
                                </div>
                                <div>
                                    <h4 style={{ margin: 0 }}>Public User</h4>
                                    <small className="muted">Find lawyers and legal advice</small>
                                </div>
                            </button>

                            <button
                                className="glass-card"
                                onClick={() => handleRoleSelect('lawyer')}
                                style={{
                                    display: 'flex', alignItems: 'center', gap: '15px', padding: '20px',
                                    cursor: 'pointer', border: '1px solid rgba(255,255,255,0.1)',
                                    background: 'rgba(255,255,255,0.05)', textAlign: 'left'
                                }}
                            >
                                <div style={{ background: 'var(--color-accent)', padding: '10px', borderRadius: '50%' }}>
                                    <FaGavel color="white" />
                                </div>
                                <div>
                                    <h4 style={{ margin: 0 }}>Legal Professional</h4>
                                    <small className="muted">Connect with clients</small>
                                </div>
                            </button>
                        </div>
                        <div style={{ textAlign: 'center', marginTop: '20px' }}>
                            <Link to="/login" style={{ color: 'var(--color-primary)' }}>Already have an account? Login</Link>
                        </div>
                    </div>
                )}

                {/* STEP 2: AUTH METHOD */}
                {step === 2 && (
                    <div className="fade-in" style={{ textAlign: 'center' }}>
                        <p style={{ marginBottom: '20px' }}>
                            Registering as <strong>{role === 'lawyer' ? 'Lawyer' : 'Public User'}</strong>
                        </p>

                        <button
                            onClick={handleGoogleSignIn}
                            disabled={loading}
                            className="btn"
                            style={{
                                background: 'white', color: '#333', width: '100%',
                                display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '10px',
                                padding: '12px', fontWeight: 'bold', marginBottom: '15px'
                            }}
                        >
                            <FaGoogle color="#DB4437" /> Continue with Google
                        </button>

                        <div className="divider" style={{ marginBottom: '15px', color: 'var(--text-muted)' }}>OR</div>

                        <button
                            onClick={selectEmailAuth}
                            className="btn secondary"
                            style={{
                                width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '10px',
                                padding: '12px', fontWeight: 'bold'
                            }}
                        >
                            <FaEnvelope /> Sign up with Email
                        </button>

                        <div style={{ marginTop: '20px' }}>
                            <button onClick={() => setStep(1)} className="btn link-btn" style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Back</button>
                        </div>
                    </div>
                )}

                {/* STEP 3: DETAILS */}
                {step === 3 && (
                    <div className="fade-in">
                        <form onSubmit={handleSubmit}>
                            {authMethod === 'email' && (
                                <div style={{ marginBottom: '15px' }}>
                                    <label style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Email</label>
                                    <input
                                        type="email"
                                        className="glass-input"
                                        value={formData.email}
                                        onChange={e => setFormData({ ...formData, email: e.target.value })}
                                        required
                                        placeholder="Enter your email"
                                    />
                                </div>
                            )}

                            {authMethod === 'google' && (
                                <div style={{ marginBottom: '15px' }}>
                                    <label style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Email</label>
                                    <input
                                        className="glass-input"
                                        value={formData.email}
                                        disabled
                                        style={{ opacity: 0.7, cursor: 'not-allowed' }}
                                    />
                                </div>
                            )}

                            <div style={{ marginBottom: '15px' }}>
                                <label style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Full Name</label>
                                <input
                                    className="glass-input"
                                    value={formData.name}
                                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                                    required
                                    placeholder="Enter your name"
                                />
                            </div>

                            {authMethod === 'email' && (
                                <div style={{ marginBottom: '15px' }}>
                                    <label style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Password</label>
                                    <input
                                        type="password"
                                        className="glass-input"
                                        value={formData.password}
                                        onChange={e => setFormData({ ...formData, password: e.target.value })}
                                        required
                                        minLength={6}
                                        placeholder="Create a password (min 6 chars)"
                                    />
                                </div>
                            )}

                            {role === 'lawyer' && (
                                <div style={{ marginBottom: '15px' }}>
                                    <label style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Bar Council ID</label>
                                    <input
                                        className="glass-input"
                                        value={formData.barCouncilId}
                                        onChange={e => setFormData({ ...formData, barCouncilId: e.target.value })}
                                        required
                                        placeholder="e.g. MH/1234/2020"
                                    />
                                </div>
                            )}

                            <button type="submit" className="btn primary" style={{ width: '100%' }} disabled={loading}>
                                {loading ? 'Creating Account...' : 'Complete Registration'}
                            </button>
                        </form>
                        <div style={{ textAlign: 'center', marginTop: '15px' }}>
                            <button onClick={() => setStep(2)} className="btn link-btn" style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Back</button>
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
};

export default Register;
