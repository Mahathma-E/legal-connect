import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const Login = ({ setUser }) => {
  const [emailOrBar, setEmailOrBar] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(
        '/login',
        { emailOrBar, password },
        { withCredentials: true }
      );
      setUser(res.data.user);
      if (res.data.user.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/home');
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Error logging in');
    }
  };

  return (
    <div className="auth-container">
      <div className="glass-card auth-box">
        <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>Login</h2>
        {error && <p style={{ color: 'var(--color-danger)', textAlign: 'center', marginBottom: '15px' }}>{error}</p>}
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Email or Bar Code"
            value={emailOrBar}
            onChange={(e) => setEmailOrBar(e.target.value)}
            required
            className="glass-input"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="glass-input"
          />
          <button type="submit" className="btn primary" style={{ width: '100%', marginTop: '10px' }}>Login</button>
        </form>
        <p style={{ textAlign: 'center', marginTop: '20px' }}>
          New here? <br />
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', marginTop: '10px' }}>
            <Link to="/register-public" className="btn secondary" style={{ fontSize: '0.8rem' }}>Public Sign Up</Link>
            <Link to="/register-lawyer" className="btn secondary" style={{ fontSize: '0.8rem' }}>Lawyer Sign Up</Link>
          </div>
        </p>
      </div>
    </div>
  );
};

export default Login;


