import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { signInWithPopup, signInWithEmailAndPassword, sendEmailVerification } from 'firebase/auth';
import { auth, googleProvider } from '../firebase';
import { FaGoogle } from 'react-icons/fa';

const Login = ({ setUser }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [emailNotVerified, setEmailNotVerified] = useState(false);
  const [resendingEmail, setResendingEmail] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setEmailNotVerified(false);
    setLoading(true);

    try {
      // Step 1: Sign in with Firebase
      console.log('[FIREBASE] Signing in with email:', email);
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;

      console.log('[FIREBASE] Signed in, UID:', user.uid, 'Email verified:', user.emailVerified);

      // Step 2: Check if email is verified
      if (!user.emailVerified) {
        setEmailNotVerified(true);
        setError('Please verify your email before logging in. Check your inbox for the verification link.');
        setLoading(false);
        return;
      }

      // Step 3: Get Firebase ID token (force refresh to get a fresh token)
      const token = await user.getIdToken(true); // true = force refresh
      console.log('[FIREBASE] Got fresh ID token');

      // Step 4: Login to backend with Firebase token
      const res = await axios.post('/login', { firebaseToken: token });

      console.log('[BACKEND] Login successful');
      setUser(res.data.user);

      if (res.data.user.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/home');
      }
    } catch (err) {
      console.error('[ERROR]', err);

      // Handle Firebase errors
      if (err.code === 'auth/user-not-found') {
        setError('No account found with this email. Please register first.');
      } else if (err.code === 'auth/wrong-password' || err.code === 'auth/invalid-credential') {
        setError('Incorrect password or email. Please try again.');
      } else if (err.code === 'auth/invalid-email') {
        setError('Invalid email address.');
      } else if (err.code === 'auth/too-many-requests') {
        setError('Too many failed login attempts. Please try again later.');
      } else if (err.code === 'auth/network-request-failed') {
        setError('Network error. Please check your internet connection.');
      } else {
        const errorData = err.response?.data;
        if (errorData?.emailNotVerified) {
          setEmailNotVerified(true);
        }
        setError(errorData?.error || err.message || 'Error logging in');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResendVerification = async () => {
    setResendingEmail(true);
    setError('');

    try {
      // Sign in to get the user object (needed to resend verification)
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      await sendEmailVerification(userCredential.user);

      alert('Verification email sent! Please check your inbox.');
      setError('');
    } catch (err) {
      console.error('[ERROR]', err);
      setError('Failed to resend verification email. Please try again.');
    } finally {
      setResendingEmail(false);
    }
  };


  const handleGoogleLogin = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const user = result.user;
      const token = await user.getIdToken();

      const res = await axios.post('/login', { firebaseToken: token });
      setUser(res.data.user);
      navigate(res.data.user.role === 'admin' ? '/admin' : '/home');
    } catch (err) {
      console.error(err);
      if (err.code === 'auth/user-not-found' || (err.response && err.response.status === 404)) {
        setError('Account not found. Please register first.');
      } else {
        setError('Google Sign In failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="glass-card auth-box">
        <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>Login</h2>

        {error && (
          <div style={{
            color: 'var(--color-danger)',
            textAlign: 'center',
            marginBottom: '15px',
            padding: '10px',
            backgroundColor: 'rgba(244, 67, 54, 0.1)',
            borderRadius: '8px',
            border: '1px solid rgba(244, 67, 54, 0.3)'
          }}>
            {error}
          </div>
        )}

        {emailNotVerified && (
          <div style={{
            backgroundColor: 'rgba(255, 152, 0, 0.1)',
            border: '1px solid rgba(255, 152, 0, 0.3)',
            borderRadius: '8px',
            padding: '15px',
            marginBottom: '15px',
            textAlign: 'center'
          }}>
            <p style={{ marginBottom: '10px' }}>📧 Email not verified</p>
            <button
              onClick={handleResendVerification}
              disabled={resendingEmail || !email || !password}
              className="btn secondary"
              style={{ fontSize: '0.9rem' }}
            >
              {resendingEmail ? 'Sending...' : 'Resend Verification Email'}
            </button>
          </div>
        )}

        <button
          onClick={handleGoogleLogin}
          className="btn"
          disabled={loading}
          style={{
            background: 'white', color: '#333', width: '100%', marginBottom: '20px',
            display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '10px'
          }}
        >
          <FaGoogle color="#DB4437" /> Sign in with Google
        </button>

        <div className="divider" style={{ textAlign: 'center', marginBottom: '20px', color: 'var(--text-muted)' }}>
          <span>OR</span>
        </div>

        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email Address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="glass-input"
            disabled={loading}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="glass-input"
            disabled={loading}
          />
          <button type="submit" className="btn primary" style={{ width: '100%', marginTop: '10px' }} disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '15px' }}>
          <Link to="/forgot-password" style={{ color: 'var(--color-primary)', textDecoration: 'none', fontSize: '0.9rem' }}>
            Forgot Password?
          </Link>
        </div>

        <p style={{ textAlign: 'center', marginTop: '20px' }}>
          New here? <Link to="/register" style={{ color: 'var(--color-primary)', fontWeight: 'bold' }}>Create an account</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;


