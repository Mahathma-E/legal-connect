import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { createUserWithEmailAndPassword, sendEmailVerification } from 'firebase/auth';
import { auth } from '../firebase';

const RegisterPublic = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);

    try {
      // Step 1: Create Firebase user
      console.log('[FIREBASE] Creating user with email:', email);
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;

      console.log('[FIREBASE] User created with UID:', user.uid);

      // Step 2: Send email verification
      await sendEmailVerification(user);
      console.log('[FIREBASE] Verification email sent to:', email);

      // Step 3: Register in backend
      await axios.post('/register', {
        firebaseUid: user.uid,
        email: email,
        name: name,
        role: 'public'
      });

      console.log('[BACKEND] User registered successfully');
      setSuccess(true);
    } catch (err) {
      console.error('[ERROR]', err);

      // Handle Firebase errors
      if (err.code === 'auth/email-already-in-use') {
        setError('This email is already registered. Please login instead.');
      } else if (err.code === 'auth/weak-password') {
        setError('Password should be at least 6 characters long.');
      } else if (err.code === 'auth/invalid-email') {
        setError('Invalid email address.');
      } else {
        setError(err.response?.data?.error || err.message || 'Error registering');
      }
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="auth-container">
        <div className="auth-box">
          <div className="glass-card" style={{ textAlign: 'center', padding: '40px 20px' }}>
            <div style={{ fontSize: '60px', marginBottom: '20px' }}>✅</div>
            <h2 style={{ color: 'var(--color-success)', marginBottom: '15px' }}>Registration Successful!</h2>
            <p style={{ marginBottom: '20px' }}>
              📧 We've sent a verification email to <strong>{email}</strong>
            </p>
            <div style={{
              backgroundColor: 'rgba(102, 126, 234, 0.1)',
              border: '1px solid rgba(102, 126, 234, 0.3)',
              borderRadius: '8px',
              padding: '20px',
              marginBottom: '20px'
            }}>
              <p style={{ marginBottom: '10px' }}>
                <strong>Next Steps:</strong>
              </p>
              <ol style={{ textAlign: 'left', paddingLeft: '20px' }}>
                <li>Check your email inbox (including spam folder)</li>
                <li>Click the verification link from Firebase</li>
                <li>Return here to log in</li>
              </ol>
            </div>
            <p className="muted" style={{ fontSize: '0.9rem' }}>
              The verification email is sent automatically by Firebase.
            </p>
            <Link to="/" className="btn primary" style={{ marginTop: '20px', display: 'inline-block' }}>
              Go to Login
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-box">
        <div className="glass-card" style={{ textAlign: 'center' }}>
          <h2 style={{ marginBottom: '20px', background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', fontSize: '2rem' }}> Create Account </h2>
          <p className="muted" style={{ marginBottom: '30px' }}>Join as a Public User</p>

          {error && <div className="alert error" style={{ marginBottom: '20px', color: 'var(--color-danger)', padding: '10px', backgroundColor: 'rgba(244, 67, 54, 0.1)', borderRadius: '8px' }}>{error}</div>}

          <form onSubmit={handleSubmit}>
            <input
              type="text"
              placeholder="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              disabled={loading}
            />
            <input
              type="email"
              placeholder="Email Address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />
            <input
              type="password"
              placeholder="Password (min 6 characters)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              disabled={loading}
            />
            <button type="submit" className="btn primary" style={{ width: '100%', marginTop: '10px' }} disabled={loading}>
              {loading ? 'Creating Account...' : 'Register'}
            </button>
          </form>

          <div style={{ marginTop: '20px', fontSize: '0.9rem' }}>
            Already have an account? <Link to="/" style={{ color: 'var(--color-primary)', fontWeight: 'bold' }}>Login</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPublic;
