import React, { useState, useEffect } from 'react';
import { Link, useNavigate, NavLink } from 'react-router-dom';
import axios from 'axios';
import { FaBell, FaSun, FaMoon, FaEnvelope, FaGlobeAmericas, FaSignOutAlt, FaBook, FaUserShield } from 'react-icons/fa';
import './Header.css';

const Header = ({ darkMode, setDarkMode, user, setUser, showDMs, setShowDMs }) => {
  const [notifications, setNotifications] = useState([]);
  const [showNotifs, setShowNotifs] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const navigate = useNavigate();

  // Search users
  useEffect(() => {
    const searchUsers = async () => {
      if (searchQuery.trim().length < 2) {
        setSearchResults([]);
        setShowSearchResults(false);
        return;
      }

      setIsSearching(true);
      try {
        const { data } = await axios.get(`/users/search?q=${encodeURIComponent(searchQuery)}`);
        setSearchResults(data || []);
        setShowSearchResults(true);
      } catch (err) {
        console.error('Error searching users:', err);
        setSearchResults([]);
      }
      setIsSearching(false);
    };

    const debounce = setTimeout(searchUsers, 300);
    return () => clearTimeout(debounce);
  }, [searchQuery]);

  useEffect(() => {
    if (!user) return;
    const fetchNotifs = async () => {
      const { data } = await axios.get(`/notifications/${user.id}`);
      setNotifications(data || []);
    };
    fetchNotifs();
    const t = setInterval(fetchNotifs, 10000);
    return () => clearInterval(t);
  }, [user]);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (!e.target.closest('.dropdown-panel') && !e.target.closest('.profile-avatar') && !e.target.closest('.icon-btn')) {
        setShowNotifs(false);
        setShowProfileMenu(false);
        setShowSearchResults(false);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    navigate('/');
  };

  const toggleNotifs = async () => {
    if (!showNotifs && notifications.length > 0) {
      try {
        await axios.delete(`/notifications/${user.id}`);
        setNotifications([]);
      } catch (e) {
        console.error(e);
      }
    }
    setShowNotifs(!showNotifs);
  };

  return (
    <header className="header">
      <div className="container nav-container">
        {/* Logo */}
        <Link to={user ? '/home' : '/'} className="logo">
          ⚖️ LegalConnect
        </Link>

        {/* Search Bar */}
        {user && (
          <div className="search-container">
            <input
              type="text"
              className="search-input"
              placeholder="🔍 Search users..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => searchResults.length > 0 && setShowSearchResults(true)}
            />

            {showSearchResults && searchResults.length > 0 && (
              <div className="search-results">
                {searchResults.map((result) => (
                  <div
                    key={result.id}
                    className="search-result-item"
                    onClick={() => {
                      navigate(`/profile/${result.id}`);
                      setSearchQuery('');
                      setShowSearchResults(false);
                    }}
                  >
                    <img
                      src={result.avatar || '/default-avatar.png'}
                      alt={result.name}
                      className="search-result-avatar"
                    />
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '5px' }}>
                        {result.name}
                        {result.isVerified && <span style={{ color: 'var(--color-primary)' }}>✓</span>}
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        {result.role} • {result.email}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Center Navigation */}
        {user && (
          <div className="nav-links nav-center">
            <NavLink
              to="/home"
              className={({ isActive }) => `nav-item ${isActive && !showDMs ? 'active' : ''}`}
              onClick={() => setShowDMs(false)}
            >
              <FaGlobeAmericas /> <span>Feed</span>
            </NavLink>
            <div
              className={`nav-item ${showDMs ? 'active' : ''}`}
              onClick={() => { setShowDMs(true); navigate('/dms'); }}
            >
              <FaEnvelope /> <span>Messages</span>
            </div>
            {user.role === 'admin' && (
              <NavLink
                to="/admin"
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                onClick={() => setShowDMs(false)}
              >
                <FaUserShield /> <span>Admin</span>
              </NavLink>
            )}
          </div>
        )}

        {/* Right Navigation */}
        {user ? (
          <div className="nav-links nav-right">
            {/* Constitution Link */}
            <NavLink
              to="/constitution"
              className={({ isActive }) => `nav-item constitution-link ${isActive ? 'active' : ''}`}
            >
              <FaBook /> <span>Constitution</span>
            </NavLink>

            {/* Notifications */}
            <div style={{ position: 'relative' }}>
              <button className="icon-btn" onClick={toggleNotifs}>
                <FaBell />
                {notifications.length > 0 && (
                  <span className="notification-badge">
                    {notifications.length}
                  </span>
                )}
              </button>

              {showNotifs && (
                <div className="dropdown-panel">
                  <h4>Notifications</h4>
                  {!notifications.length && <p style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No new notifications</p>}
                  {notifications.map((n, i) => (
                    <div key={i} style={{ padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.05)', fontSize: '0.9rem' }}>
                      <strong style={{ color: 'var(--color-primary)' }}>{n.type}</strong> from {n.fromName || n.from}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Profile Menu */}
            <div style={{ position: 'relative' }}>
              <img
                src={user.avatar || '/default-avatar.png'}
                alt="avatar"
                className="profile-avatar"
                onClick={() => setShowProfileMenu(!showProfileMenu)}
              />

              {showProfileMenu && (
                <div className="dropdown-panel" style={{ right: 0, width: '200px' }}>
                  <div
                    onClick={() => {
                      navigate(`/profile/${user.id}`);
                      setShowProfileMenu(false);
                    }}
                    style={{
                      padding: '12px',
                      cursor: 'pointer',
                      borderRadius: '8px',
                      marginBottom: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      transition: 'background 0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <img
                      src={user.avatar || '/default-avatar.png'}
                      alt="avatar"
                      style={{ width: '32px', height: '32px', borderRadius: '50%' }}
                    />
                    <div>
                      <div style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>{user.name}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>View Profile</div>
                    </div>
                  </div>
                  <div
                    onClick={() => {
                      handleLogout();
                      setShowProfileMenu(false);
                    }}
                    style={{
                      padding: '12px',
                      cursor: 'pointer',
                      borderRadius: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      color: 'var(--color-danger)',
                      transition: 'background 0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 118, 117, 0.1)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <FaSignOutAlt />
                    <span>Logout</span>
                  </div>
                </div>
              )}
            </div>

            {/* Theme Toggle */}
            <button
              className="icon-btn"
              onClick={() => setDarkMode(!darkMode)}
              title="Toggle Theme"
            >
              {darkMode ? <FaSun /> : <FaMoon />}
            </button>
          </div>
        ) : (
          <button
            className="icon-btn"
            onClick={() => setDarkMode(!darkMode)}
            title="Toggle Theme"
          >
            {darkMode ? <FaSun /> : <FaMoon />}
          </button>
        )}
      </div>
    </header>
  );
};

export default Header;
