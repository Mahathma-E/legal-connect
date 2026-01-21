import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

const RegisterPublic = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/register', {
        email,
        password,
        name,
        role: 'public'
      });
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Error registering');
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <div className="glass-card" style={{ textAlign: 'center' }}>
          <h2 style={{ marginBottom: '20px', background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', fontSize: '2rem' }}> Create Account </h2>
          <p className="muted" style={{ marginBottom: '30px' }}>Join as a Public User</p>

          {error && <div className="alert error" style={{ marginBottom: '20px', color: 'var(--color-danger)' }}>{error}</div>}

          <form onSubmit={handleSubmit}>
            <input
              type="text"
              placeholder="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
            <input
              type="email"
              placeholder="Email Address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button type="submit" className="btn primary" style={{ width: '100%', marginTop: '10px' }}>Register</button>
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