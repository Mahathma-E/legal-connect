import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import RegisterPublic from './components/RegisterPublic';
import RegisterLawyer from './components/RegisterLawyer';
import Home from './components/Home';
import Profile from './components/Profile';
import Chatbot from './components/Chatbot';
import DM from './components/DM';
import Header from './components/Header';
import './App.css';

import ChatPage from './components/ChatPage';
import Constitution from './components/Constitution';
import AdminDashboard from './components/AdminDashboard';
import VerifyEmail from './components/VerifyEmail';
import ForgotPassword from './components/ForgotPassword';
import ResetPassword from './components/ResetPassword';

const App = () => {
  const [darkMode, setDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [user, setUser] = useState(() => {
    const u = localStorage.getItem('user');
    return u ? JSON.parse(u) : null;
  });
  const [showDMs, setShowDMs] = useState(false);

  useEffect(() => {
    document.documentElement.dataset.theme = darkMode ? 'dark' : 'light';
    localStorage.setItem('darkMode', darkMode ? 'true' : 'false');
  }, [darkMode]);

  return (
    <div className="app-root">
      <Router>
        <Header darkMode={darkMode} setDarkMode={setDarkMode} user={user} setUser={setUser} showDMs={showDMs} setShowDMs={setShowDMs} />
        <Routes>
          <Route path="/" element={user ? <Navigate to="/home" /> : <Login setUser={(u) => { setUser(u); localStorage.setItem('user', JSON.stringify(u)); }} />} />
          <Route path="/login" element={user ? <Navigate to="/home" /> : <Login setUser={(u) => { setUser(u); localStorage.setItem('user', JSON.stringify(u)); }} />} />
          <Route path="/register" element={<Register setUser={(u) => { setUser(u); localStorage.setItem('user', JSON.stringify(u)); }} />} />
          <Route path="/register-public" element={<RegisterPublic />} />
          <Route path="/register-lawyer" element={<RegisterLawyer />} />
          <Route path="/verify-email/:token" element={<VerifyEmail />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password/:token" element={<ResetPassword />} />
          <Route path="/home" element={user ? <Home user={user} showDMs={showDMs} /> : <Navigate to="/" />} />
          <Route path="/profile/:id" element={user ? <Profile user={user} setUser={setUser} /> : <Navigate to="/" />} />
          <Route path="/dm/:convId" element={user ? <DM user={user} /> : <Navigate to="/" />} />
          <Route path="/dms" element={user ? <DM user={user} /> : <Navigate to="/" />} />
          <Route path="/ai-assistant" element={user ? <ChatPage /> : <Navigate to="/" />} />
          <Route path="/constitution" element={user ? <Constitution /> : <Navigate to="/" />} />
          <Route path="/admin" element={user && user.role === 'admin' ? <AdminDashboard user={user} /> : <Navigate to="/" />} />
        </Routes>
        {user && <Chatbot />}
      </Router>
    </div>
  );
};

export default App;
