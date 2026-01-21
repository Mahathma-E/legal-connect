import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { FaCheckCircle } from 'react-icons/fa';

const UserListModal = ({ title, userIds, onClose }) => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUsers = async () => {
            if (!userIds || userIds.length === 0) {
                setUsers([]);
                return;
            }
            setLoading(true);
            try {
                // Optimization: In a real app, we'd have a batch endpoint.
                // For now, we will fetch the full user list and filter client-side 
                // OR fetch individually. Given the potential size, let's fetch all (since the backend has a GET /users endpoint)
                // and filter. A proper backend would support filtering.
                const { data } = await axios.get('/users');
                const filtered = data.filter(u => userIds.includes(u.id));
                setUsers(filtered);
            } catch (err) {
                console.error("Error fetching user list details:", err);
            }
            setLoading(false);
        };

        fetchUsers();
    }, [userIds]);

    const handleNavigate = (id) => {
        onClose();
        navigate(`/profile/${id}`);
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="glass-card modal" onClick={e => e.stopPropagation()}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <h3>{title}</h3>
                    <button className="btn secondary" style={{ padding: '5px 10px' }} onClick={onClose}>X</button>
                </div>

                {loading ? (
                    <div style={{ textAlign: 'center', padding: '20px' }}>Loading...</div>
                ) : users.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-muted)' }}>No users found.</div>
                ) : (
                    <div className="user-list">
                        {users.map(u => (
                            <div key={u.id} className="user-list-item">
                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }} onClick={() => handleNavigate(u.id)}>
                                    <img src={u.avatar || '/default-avatar.png'} alt={u.name} className="avatar-sm" />
                                    <div>
                                        <div style={{ fontWeight: '600', display: 'flex', alignItems: 'center', gap: '5px' }}>
                                            {u.name}
                                            {u.role === 'lawyer' && u.isVerified && <FaCheckCircle style={{ color: 'var(--color-primary)', fontSize: '0.8rem' }} title="Verified User" />}
                                        </div>
                                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{u.role}</div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default UserListModal;
