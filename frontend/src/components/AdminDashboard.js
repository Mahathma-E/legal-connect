import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { FaTrash, FaCheckCircle, FaTimesCircle, FaUserShield, FaEye, FaTimes } from 'react-icons/fa';

const AdminDashboard = ({ user }) => {
    const [users, setUsers] = useState([]);
    const [requests, setRequests] = useState([]);
    const [viewProof, setViewProof] = useState(null); // { url: string, type: 'image' | 'pdf' | 'other' }

    const fetchData = async () => {
        try {
            const usersRes = await axios.get('/admin/users', { headers: { 'X-User-Id': user.id } });
            setUsers(usersRes.data);

            const reqRes = await axios.get('/admin/verification-requests', { headers: { 'X-User-Id': user.id } });
            setRequests(reqRes.data);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleDelete = async (uid, name) => {
        if (window.confirm(`Are you sure you want to delete user "${name}"? This action cannot be undone.`)) {
            try {
                await axios.delete(`/admin/users/${uid}`, { headers: { 'X-User-Id': user.id } });
                setUsers(users.filter(u => u.id !== uid));
            } catch (err) {
                alert("Failed to delete user");
            }
        }
    };

    const handleVerifyUserDirectly = async (uid) => {
        try {
            const { data } = await axios.post(`/admin/users/${uid}/verify`, {}, { headers: { 'X-User-Id': user.id } });
            setUsers(users.map(u => u.id === uid ? { ...u, isVerified: data.isVerified } : u));
        } catch (err) {
            alert("Failed to update status");
        }
    };

    const handleApproveRequest = async (rid) => {
        try {
            await axios.post(`/admin/verification-requests/${rid}/approve`, {}, { headers: { 'X-User-Id': user.id } });
            // Optimistically update
            setRequests(requests.filter(r => r.id !== rid));
            // Also refresh users list to show the new badge immediately
            const usersRes = await axios.get('/admin/users', { headers: { 'X-User-Id': user.id } });
            setUsers(usersRes.data);
            alert("Request Approved and User Verified!");
        } catch (err) {
            alert("Failed to approve request");
        }
    };

    const handleRejectRequest = async (rid) => {
        if (!window.confirm("Reject this verification request?")) return;
        try {
            await axios.post(`/admin/verification-requests/${rid}/reject`, {}, { headers: { 'X-User-Id': user.id } });
            setRequests(requests.filter(r => r.id !== rid));
        } catch (err) {
            alert("Failed to reject request");
        }
    };

    const openProof = (url) => {
        if (!url) return;
        const ext = url.split('.').pop().toLowerCase();
        let type = 'other';
        if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) {
            type = 'image';
        } else if (ext === 'pdf') {
            type = 'pdf';
        }
        setViewProof({ url, type });
    };

    const closeProof = () => {
        setViewProof(null);
    };

    return (
        <div className="container">
            {/* Proof Modal */}
            {viewProof && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    zIndex: 1000,
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    padding: '20px'
                }}>
                    <div style={{
                        position: 'relative',
                        background: '#1a1a1a',
                        padding: '10px',
                        borderRadius: '8px',
                        maxWidth: '90%',
                        maxHeight: '90%',
                        display: 'flex',
                        flexDirection: 'column',
                        overflow: 'hidden'
                    }}>
                        <button
                            onClick={closeProof}
                            style={{
                                position: 'absolute',
                                top: '10px',
                                right: '10px',
                                background: 'red',
                                border: 'none',
                                color: 'white',
                                borderRadius: '50%',
                                width: '30px',
                                height: '30px',
                                cursor: 'pointer',
                                zIndex: 10
                            }}
                        >
                            <FaTimes />
                        </button>

                        <div style={{ overflow: 'auto', flex: 1, display: 'flex', justifyContent: 'center' }}>
                            {viewProof.type === 'image' ? (
                                <img src={viewProof.url} alt="Proof" style={{ maxWidth: '100%', maxHeight: '80vh', objectFit: 'contain' }} />
                            ) : (
                                <iframe src={viewProof.url} title="Proof Document" style={{ width: '80vw', height: '80vh', border: 'none' }} />
                            )}
                        </div>
                        {viewProof.type === 'other' && (
                            <div style={{ textAlign: 'center', marginTop: '10px', color: 'white' }}>
                                <p>Cannot preview this file type.</p>
                                <a href={viewProof.url} download className="btn primary">Download File</a>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Pending Requests Section */}
            {requests.length > 0 && (
                <div className="glass-card" style={{ marginBottom: '30px', borderLeft: '4px solid var(--color-accent)' }}>
                    <h3 style={{ marginBottom: '20px' }}>Pending Verification Requests</h3>
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ background: 'rgba(255,255,255,0.05)', textAlign: 'left' }}>
                                    <th style={{ padding: '10px' }}>Lawyer</th>
                                    <th style={{ padding: '10px' }}>Bar ID</th>
                                    <th style={{ padding: '10px' }}>Document</th>
                                    <th style={{ padding: '10px' }}>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {requests.map(r => (
                                    <tr key={r.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                        <td style={{ padding: '10px' }}>
                                            <div style={{ fontWeight: 'bold' }}>{r.name}</div>
                                            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{r.email}</div>
                                        </td>
                                        <td style={{ padding: '10px' }}>{r.barCode}</td>
                                        <td style={{ padding: '10px' }}>
                                            {r.documentUrl ? (
                                                <button
                                                    onClick={() => openProof(r.documentUrl)}
                                                    className="btn secondary"
                                                    style={{ fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '5px' }}
                                                >
                                                    <FaEye /> View Proof
                                                </button>
                                            ) : (
                                                <span className="muted">No Proof</span>
                                            )}
                                        </td>
                                        <td style={{ padding: '10px' }}>
                                            <div style={{ display: 'flex', gap: '10px' }}>
                                                <button className="btn primary" style={{ fontSize: '0.8rem', padding: '5px 10px' }} onClick={() => handleApproveRequest(r.id)}>
                                                    Approve
                                                </button>
                                                <button className="btn danger" style={{ fontSize: '0.8rem', padding: '5px 10px' }} onClick={() => handleRejectRequest(r.id)}>
                                                    Reject
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            <div className="glass-card">
                <h2 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <FaUserShield style={{ color: 'var(--color-accent)' }} /> User Management
                </h2>
                <p className="muted">Manage users and lawyer verification status directly.</p>

                <div style={{ marginTop: '30px', overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '600px' }}>
                        <thead>
                            <tr style={{ background: 'rgba(255,255,255,0.05)', textAlign: 'left' }}>
                                <th style={{ padding: '15px' }}>User</th>
                                <th style={{ padding: '15px' }}>Role</th>
                                <th style={{ padding: '15px' }}>Status</th>
                                <th style={{ padding: '15px' }}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(u => (
                                <tr key={u.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                    <td style={{ padding: '15px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                        <img src={u.avatar} alt="avatar" className="avatar-sm" />
                                        <div>
                                            <div style={{ fontWeight: 'bold' }}>{u.name}</div>
                                            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{u.email}</div>
                                        </div>
                                    </td>
                                    <td style={{ padding: '15px' }}>
                                        <span style={{
                                            padding: '4px 8px',
                                            borderRadius: '4px',
                                            background: u.role === 'lawyer' ? 'rgba(108, 92, 231, 0.2)' : 'rgba(255,255,255,0.1)',
                                            color: u.role === 'lawyer' ? 'var(--color-primary)' : 'inherit',
                                            fontSize: '0.85rem',
                                            fontWeight: '600',
                                            textTransform: 'uppercase'
                                        }}>
                                            {u.role}
                                        </span>
                                    </td>
                                    <td style={{ padding: '15px' }}>
                                        {u.role === 'lawyer' ? (
                                            u.isVerified ? (
                                                <span style={{ color: 'var(--color-success)', display: 'flex', alignItems: 'center', gap: '5px' }}>
                                                    <FaCheckCircle /> Verified
                                                </span>
                                            ) : (
                                                <span style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '5px' }}>
                                                    <FaTimesCircle /> Unverified
                                                </span>
                                            )
                                        ) : (
                                            <span className="muted">-</span>
                                        )}
                                    </td>
                                    <td style={{ padding: '15px' }}>
                                        <div style={{ display: 'flex', gap: '10px' }}>
                                            {u.role === 'lawyer' && (
                                                <button
                                                    className="btn secondary"
                                                    style={{ padding: '5px 10px', fontSize: '0.8rem' }}
                                                    onClick={() => handleVerifyUserDirectly(u.id)}
                                                >
                                                    {u.isVerified ? 'Revoke' : 'Toggle'}
                                                </button>
                                            )}

                                            {u.role !== 'admin' && (
                                                <button
                                                    className="btn danger"
                                                    style={{ padding: '5px 10px', fontSize: '0.8rem' }}
                                                    onClick={() => handleDelete(u.id, u.name)}
                                                    title="Delete User"
                                                >
                                                    <FaTrash />
                                                </button>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
