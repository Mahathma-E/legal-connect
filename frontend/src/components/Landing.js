import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { signInWithPopup, signInWithEmailAndPassword } from 'firebase/auth';
import { auth, googleProvider } from '../firebase';
import axios from 'axios';
import { FaGoogle, FaTimes } from 'react-icons/fa';
import './Landing.css';

const Landing = ({ setUser }) => {
    const navigate = useNavigate();

    // State for Modal and Flow
    const [showModal, setShowModal] = useState(false);
    const [modalMode, setModalMode] = useState('register'); // 'register' | 'login'

    // Register State
    const [registerStep, setRegisterStep] = useState(1); // 1: Role, 2: Details
    const [role, setRole] = useState(null); // 'public' | 'lawyer'

    // Login State
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Form Data for Registration Step 2
    const [formData, setFormData] = useState({
        name: '',
        barCouncilId: '',
        userId: '', // stores firebase email or other id
        email: '',
        firebaseUid: '',
        photoUrl: ''
    });

    // --- MODAL CONTROLS ---
    const openRegisterModal = () => {
        setModalMode('register');
        setRegisterStep(1);
        setRole(null);
        setError('');
        setShowModal(true);
    };

    const openLoginModal = () => {
        setModalMode('login');
        setError('');
        setEmail('');
        setPassword('');
        setShowModal(true);
    };

    const handleRoleSelect = (selectedRole) => {
        setRole(selectedRole);
    };

    // --- GOOGLE AUTH (Shared) ---
    const handleGoogleAuth = async () => {
        if (modalMode === 'register' && !role) {
            setError('Please select an account type first.');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const result = await signInWithPopup(auth, googleProvider);
            const user = result.user;
            const token = await user.getIdToken();

            try {
                // Try Login Verification first
                const loginRes = await axios.post('/login', { firebaseToken: token });
                setUser(loginRes.data.user);
                navigate(loginRes.data.user.role === 'admin' ? '/admin' : '/home');
            } catch (err) {
                // If Login fails:
                if (modalMode === 'login') {
                    // Start registration flow if user not found, 
                    // OR show error if we want strict login.
                    // Usually "Sign in with Google" acts as both. 
                    // If account doesn't exist, we should probably prompt to create one or error.
                    // Let's assume we error for now to check role? 
                    // Actually, if they try to login with Google and don't exist, better to redirect to registration logic?
                    // But we don't know their role yet. 
                    setError('Account not found. Please create an account.');
                } else {
                    // Registration Mode: New User
                    setFormData({
                        name: user.displayName || '',
                        email: user.email,
                        firebaseUid: user.uid,
                        photoUrl: user.photoURL,
                        barCouncilId: ''
                    });
                    setRegisterStep(2);
                }
            }
        } catch (err) {
            console.error(err);
            setError('Authentication failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    // --- EMAIL LOGIN (Login Mode Only) ---
    const handleEmailLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            const user = userCredential.user;
            const token = await user.getIdToken();

            const res = await axios.post('/login', { firebaseToken: token });
            setUser(res.data.user);
            navigate(res.data.user.role === 'admin' ? '/admin' : '/home');

        } catch (err) {
            console.error(err);
            if (err.code === 'auth/wrong-password' || err.code === 'auth/user-not-found' || err.code === 'auth/invalid-credential') {
                setError('Invalid email or password.');
            } else {
                setError('Login failed. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    // --- FINAL REGISTRATION SUBMIT ---
    const handleFinalRegister = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const endpoint = role === 'lawyer' ? '/register-lawyer' : '/register-public';
            const payload = {
                name: formData.name,
                email: formData.email,
                firebaseUid: formData.firebaseUid,
                ...(role === 'lawyer' && { barCouncilId: formData.barCouncilId }),
            };

            const res = await axios.post(endpoint, payload);
            setUser(res.data.user);
            navigate('/home');

        } catch (err) {
            console.error(err);
            setError(err.response?.data?.error || 'Registration failed.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="landing-container">
            <div className="landing-top-brand">Legal Connect</div>

            <div className="landing-image-section">
                <div className="landing-image-overlay"></div>
            </div>

            <div className="landing-content-section">
                <div className="landing-logo">⚖️</div>
                <h1 className="landing-title">Connect with Justice</h1>
                <h2 className="landing-subtitle">Join Legal Connect today.</h2>

                <button className="landing-btn btn-google" onClick={openRegisterModal}>
                    <FaGoogle /> Sign up with Google
                </button>

                <div className="divider">
                    <span>or</span>
                </div>

                <Link to="/register-public" className="landing-btn btn-create" style={{ textDecoration: 'none' }}>
                    Create account
                </Link>

                <div className="terms-text">
                    By signing up, you agree to the <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>, including Cookie Use.
                </div>

                <div className="signin-section">
                    <h3>Already have an account?</h3>
                    {/* UPDATED: Button triggers Modal instead of Link */}
                    <button className="landing-btn btn-outline" onClick={openLoginModal}>
                        Sign in
                    </button>
                </div>
            </div>

            {/* SHARED MODAL */}
            {showModal && (
                <div className="modal-overlay">
                    <div className="modal-content">
                        <button className="close-modal" onClick={() => setShowModal(false)}><FaTimes /></button>
                        <div className="modal-header-logo">⚖️</div>

                        {/* --- REGISTER MODE --- */}
                        {modalMode === 'register' && (
                            <>
                                {registerStep === 1 && (
                                    <>
                                        <h2 className="modal-step-title">Choose your account type</h2>
                                        <div className="role-cards">
                                            <div
                                                className={`role-card ${role === 'public' ? 'selected' : ''}`}
                                                onClick={() => handleRoleSelect('public')}
                                            >
                                                <div className="role-info">
                                                    <h4>Public User</h4>
                                                    <p>Seek legal advice.</p>
                                                </div>
                                            </div>
                                            <div
                                                className={`role-card ${role === 'lawyer' ? 'selected' : ''}`}
                                                onClick={() => handleRoleSelect('lawyer')}
                                            >
                                                <div className="role-info">
                                                    <h4>Lawyer</h4>
                                                    <p>Manage your practice.</p>
                                                </div>
                                            </div>
                                        </div>
                                        {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}
                                        <div className="step-actions">
                                            <button
                                                className="action-btn primary-btn"
                                                disabled={!role || loading}
                                                onClick={handleGoogleAuth}
                                            >
                                                {loading ? 'Connecting...' : 'Continue with Google'}
                                            </button>
                                        </div>
                                    </>
                                )}

                                {registerStep === 2 && (
                                    <form onSubmit={handleFinalRegister}>
                                        <h2 className="modal-step-title">Finish your profile</h2>
                                        <label style={{ color: '#71767b', fontSize: '0.9rem' }}>Name</label>
                                        <input
                                            className="form-input"
                                            value={formData.name}
                                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                            required
                                        />
                                        {role === 'lawyer' && (
                                            <>
                                                <label style={{ color: '#71767b', fontSize: '0.9rem' }}>Bar Council ID</label>
                                                <input
                                                    className="form-input"
                                                    value={formData.barCouncilId}
                                                    onChange={(e) => setFormData({ ...formData, barCouncilId: e.target.value })}
                                                    required
                                                    placeholder="e.g. MH/1234/2020"
                                                />
                                            </>
                                        )}
                                        <label style={{ color: '#71767b', fontSize: '0.9rem' }}>Email</label>
                                        <input className="form-input" value={formData.email} disabled style={{ opacity: 0.7 }} />
                                        {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}
                                        <div className="step-actions">
                                            <button className="action-btn primary-btn" type="submit" disabled={loading}>
                                                {loading ? 'Creating Account...' : 'Complete Registration'}
                                            </button>
                                        </div>
                                    </form>
                                )}
                            </>
                        )}

                        {/* --- LOGIN MODE --- */}
                        {modalMode === 'login' && (
                            <>
                                <h2 className="modal-step-title">Sign in to Legal Connect</h2>
                                <button className="landing-btn btn-google" onClick={handleGoogleAuth} style={{ marginBottom: '20px' }}>
                                    <FaGoogle /> Sign in with Google
                                </button>

                                <div className="divider" style={{ margin: '0 auto 20px auto' }}>
                                    <span>or</span>
                                </div>

                                <form onSubmit={handleEmailLogin}>
                                    <input
                                        className="form-input"
                                        type="email"
                                        placeholder="Email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                    />
                                    <input
                                        className="form-input"
                                        type="password"
                                        placeholder="Password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                    />

                                    {error && <p style={{ color: 'red', marginBottom: '15px' }}>{error}</p>}

                                    <button className="landing-btn btn-create" style={{ marginTop: '10px', width: '100%' }} type="submit" disabled={loading}>
                                        {loading ? 'Logging in...' : 'Sign In'}
                                    </button>
                                </form>

                                <div style={{ textAlign: 'center', marginTop: '20px' }}>
                                    <Link to="/forgot-password" style={{ color: '#1d9bf0', textDecoration: 'none', fontSize: '0.9rem' }}>
                                        Forgot password?
                                    </Link>
                                    <div style={{ marginTop: '10px', fontSize: '0.9rem', color: '#71767b' }}>
                                        Don't have an account? <span style={{ color: '#1d9bf0', cursor: 'pointer' }} onClick={openRegisterModal}>Sign up</span>
                                    </div>
                                </div>
                            </>
                        )}

                    </div>
                </div>
            )}
        </div>
    );
};

export default Landing;
