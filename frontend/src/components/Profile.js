import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import UserListModal from './UserListModal';
import VerificationRequestModal from './VerificationRequestModal';
import { FaCheckCircle } from 'react-icons/fa';

const Profile = ({ user, setUser }) => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null);
  const [bio, setBio] = useState('');
  const [uploading, setUploading] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [deleting, setDeleting] = useState(false);
  const [isFollowing, setIsFollowing] = useState(false);
  const [isFollowLoading, setIsFollowLoading] = useState(false);

  // New state for user lists
  const [modalType, setModalType] = useState(null); // 'followers' or 'following' or null

  // Verification State
  const [reqStatus, setReqStatus] = useState('none');
  const [showVerifyModal, setShowVerifyModal] = useState(false);

  // Fetch profile data
  const fetchProfile = async () => {
    try {
      const { data } = await axios.get(`/profile/${id}`, { withCredentials: true });
      setProfile(data);
      setBio(data.bio || '');

      // Check if current user follows this profile
      if (user && user.id !== id) {
        setIsFollowing(user?.following?.includes(id) || data.followers?.includes(user?.id) || false);
      }

      // Check verification request status for self
      if (user && user.id === id && data.role === 'lawyer' && !data.isVerified) {
        try {
          const sRes = await axios.get(`/users/${id}/verification-status`);
          setReqStatus(sRes.data.status);
        } catch (e) {
          console.error(e);
        }
      }
    } catch (err) {
      console.error("Error fetching profile:", err);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, [id]);

  // Handle follow/unfollow
  const handleFollowToggle = async () => {
    if (!user || user.id === id) return;

    setIsFollowLoading(true);
    try {
      const endpoint = isFollowing ? '/unfollow' : '/follow';
      await axios.post(`/users/${id}${endpoint}`, { from: user.id }, { withCredentials: true });
      setIsFollowing(!isFollowing);
      // Wait a bit to ensure backend consistency if needed, then refetch
      setTimeout(fetchProfile, 200);
    } catch (err) {
      console.error("Error toggling follow:", err);
      alert("Failed to update follow status");
    }
    setIsFollowLoading(false);
  };

  // Change avatar
  const onAvatarChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const fd = new FormData();
      fd.append('avatar', file);

      const uploadRes = await axios.post('/upload-avatar', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
        withCredentials: true
      });

      await axios.post(`/profile/${id}`, { avatar: uploadRes.data.url }, { withCredentials: true });
      await fetchProfile();

      if (user && user.id === id) {
        const updatedUser = { ...user, avatar: uploadRes.data.url };
        setUser(updatedUser);
        localStorage.setItem('user', JSON.stringify(updatedUser));
        navigate('/home', { replace: true });
      }
    } catch (err) {
      console.error("Error uploading avatar:", err);
    }
    setUploading(false);
  };

  // Save bio
  const saveBio = async () => {
    try {
      await axios.post(`/profile/${id}`, { bio }, { withCredentials: true });
      fetchProfile();
    } catch (err) {
      console.error("Error saving bio:", err);
    }
  };

  // Start direct message
  const startDM = async () => {
    try {
      const { data } = await axios.post(
        '/conversations',
        { users: [user.id, id] },
        { withCredentials: true }
      );
      navigate(`/dm/${data.id}`);
    } catch (err) {
      console.error("Error starting DM:", err);
      if (err.response?.status === 403) {
        alert("You must follow this user to send a DM.");
      } else {
        alert("Could not start DM. Please try again.");
      }
    }
  };

  // Delete account
  const handleDeleteAccount = async () => {
    if (!deletePassword.trim()) {
      alert('Please enter your password to confirm account deletion.');
      return;
    }

    if (!window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return;
    }

    setDeleting(true);
    try {
      await axios.delete(`/profile/${id}/delete`, {
        data: { password: deletePassword },
        withCredentials: true
      });

      setUser(null);
      localStorage.removeItem('user');
      navigate('/');
      alert('Your account has been deleted successfully.');
    } catch (err) {
      console.error("Error deleting account:", err);
      if (err.response?.status === 401) {
        alert('Invalid password. Please try again.');
      } else {
        alert('Error deleting account. Please try again.');
      }
    }
    setDeleting(false);
    setShowDeleteModal(false);
    setDeletePassword('');
  };

  if (!profile) {
    return (
      <div className="container" style={{ display: 'flex', justifyContent: 'center', marginTop: '50px' }}>
        <div className="glass-card" style={{ padding: '40px' }}>Loading Profile...</div>
      </div>
    );
  }

  return (
    <div className="container profile">
      <div className="glass-card profile-card">
        <div style={{ position: 'relative', display: 'inline-block' }}>
          <img
            className="avatar-lg"
            src={profile.avatar || '/default-avatar.png'}
            alt="avatar"
          />
          {user?.id === id && (
            <label className="btn secondary" style={{
              position: 'absolute',
              bottom: '10px',
              right: '-10px',
              borderRadius: '50%',
              padding: '8px',
              width: '40px',
              height: '40px',
              minWidth: 'auto'
            }}>
              <span style={{ fontSize: '1.2rem' }}>📷</span>
              <input type="file" accept="image/*" onChange={onAvatarChange} hidden />
            </label>
          )}
        </div>

        <h1 style={{ marginBottom: '5px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
          {profile.name}
          {profile.isVerified && <FaCheckCircle style={{ color: 'var(--color-primary)', fontSize: '1.2rem' }} title="Verified User" />}
        </h1>
        <p className="muted" style={{ marginBottom: '20px' }}>{profile.email} • <span style={{ textTransform: 'capitalize', color: 'var(--color-primary)' }}>{profile.role}</span></p>

        {/* Follower/Following Stats */}
        <div style={{ display: 'flex', gap: '30px', justifyContent: 'center', margin: '20px 0' }}>
          <div className="stat-box" onClick={() => setModalType('followers')}>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{profile.followers?.length || 0}</div>
            <div className="muted" style={{ fontSize: '0.9rem' }}>Followers</div>
          </div>
          <div className="stat-box" onClick={() => setModalType('following')}>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{profile.following?.length || 0}</div>
            <div className="muted" style={{ fontSize: '0.9rem' }}>Following</div>
          </div>
        </div>

        <div style={{ maxWidth: '400px', margin: '0 auto 20px' }}>
          {user?.id === id ? (
            <textarea
              className="glass-input"
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="Add a bio..."
              style={{ width: '100%', minHeight: '80px', textAlign: 'center' }}
              onBlur={saveBio}
            />
          ) : (
            <p style={{ fontStyle: 'italic', color: bio ? 'var(--text-main)' : 'var(--text-muted)' }}>
              {bio || "No bio available."}
            </p>
          )}
        </div>

        <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', marginBottom: '20px' }}>
          {user && user.id !== id && (
            <>
              <button
                className={`btn ${isFollowing ? 'secondary' : 'primary'}`}
                onClick={handleFollowToggle}
                disabled={isFollowLoading}
              >
                {isFollowLoading ? '...' : (isFollowing ? 'Unfollow' : 'Follow')}
              </button>
              <button className="btn secondary" onClick={startDM}>
                Message
              </button>
            </>
          )}

          {user?.id === id && (
            <button
              className="btn danger"
              onClick={() => setShowDeleteModal(true)}
            >
              Delete Account
            </button>
          )}
        </div>

        {/* Verification Request Action for Self */}
        {user?.id === id && profile.role === 'lawyer' && !profile.isVerified && (
          <div style={{ marginTop: '0px', textAlign: 'center' }}>
            {reqStatus === 'pending' ? (
              <div className="btn secondary" style={{ cursor: 'default', opacity: 0.8, display: 'inline-block' }}>
                Verification Pending...
              </div>
            ) : (
              <button className="btn primary" onClick={() => setShowVerifyModal(true)}>
                Request Verification Badge
              </button>
            )}
            {reqStatus !== 'pending' && (
              <p style={{ marginTop: '10px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Upload your Bar Council ID to get verified.
              </p>
            )}
          </div>
        )}
      </div>

      {/* User List Modal */}
      {modalType && (
        <UserListModal
          title={modalType === 'followers' ? 'Followers' : 'Following'}
          userIds={modalType === 'followers' ? profile.followers : profile.following}
          onClose={() => setModalType(null)}
        />
      )}

      {/* Verification Modal */}
      {showVerifyModal && (
        <VerificationRequestModal
          user={user}
          onClose={() => setShowVerifyModal(false)}
        />
      )}

      {/* Delete Account Modal */}
      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="glass-card modal">
            <h3 style={{ color: 'var(--color-danger)' }}>Delete Account</h3>
            <p style={{ margin: '15px 0' }}>This action cannot be undone. All your data will be permanently deleted.</p>

            <div className="form-group">
              <label>Enter your password to confirm:</label>
              <input
                type="password"
                value={deletePassword}
                onChange={(e) => setDeletePassword(e.target.value)}
                placeholder="Password"
              />
            </div>

            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px' }}>
              <button
                className="btn secondary"
                onClick={() => {
                  setShowDeleteModal(false);
                  setDeletePassword('');
                }}
                disabled={deleting}
              >
                Cancel
              </button>
              <button
                className="btn danger"
                onClick={handleDeleteAccount}
                disabled={deleting}
              >
                {deleting ? 'Deleting...' : 'Delete Forever'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
