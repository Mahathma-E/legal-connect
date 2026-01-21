import React, { useState } from 'react';
import axios from 'axios';
import { FaTimes, FaFileUpload, FaPaperPlane } from 'react-icons/fa';

const VerificationRequestModal = ({ user, onClose }) => {
    const [name, setName] = useState(user.name || '');
    const [email, setEmail] = useState(user.email || '');
    const [barCode, setBarCode] = useState(user.bar_code || '');
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            alert("Please upload your Bar Code document.");
            return;
        }

        setUploading(true);
        const formData = new FormData();
        formData.append('userId', user.id);
        formData.append('name', name);
        formData.append('email', email);
        formData.append('barCode', barCode);
        formData.append('document', file);

        try {
            await axios.post('/verification-request', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setSuccess(true);
            setTimeout(() => {
                onClose();
                window.location.reload(); // To update pending status (simple way)
            }, 2000);
        } catch (err) {
            console.error(err);
            alert(err.response?.data?.error || "Failed to submit request.");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="glass-card modal" style={{ maxWidth: '500px', width: '90%' }}>
                <button className="close-btn" onClick={onClose}><FaTimes /></button>

                {success ? (
                    <div style={{ textAlign: 'center', padding: '20px' }}>
                        <h2 style={{ color: 'var(--color-success)' }}>Request Sent!</h2>
                        <p>Your verification request has been submitted to the admin.</p>
                    </div>
                ) : (
                    <form onSubmit={handleSubmit}>
                        <h2 style={{ marginBottom: '20px' }}>Request Verification</h2>
                        <p className="muted" style={{ marginBottom: '20px' }}>
                            Submit your details and Bar Council ID proof to get the verified badge.
                        </p>

                        <div style={{ marginBottom: '15px' }}>
                            <label>Full Name</label>
                            <input
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                                className="glass-input"
                            />
                        </div>

                        <div style={{ marginBottom: '15px' }}>
                            <label>Email</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                className="glass-input"
                            />
                        </div>

                        <div style={{ marginBottom: '15px' }}>
                            <label>Bar Code ID</label>
                            <input
                                type="text"
                                value={barCode}
                                onChange={(e) => setBarCode(e.target.value)}
                                required
                                className="glass-input"
                            />
                        </div>

                        <div style={{ marginBottom: '20px' }}>
                            <label>Upload Bar Code Document</label>
                            <div style={{
                                border: '1px dashed var(--color-primary)',
                                padding: '20px',
                                borderRadius: '10px',
                                textAlign: 'center',
                                marginTop: '5px',
                                cursor: 'pointer',
                                background: 'rgba(255,255,255,0.05)'
                            }} onClick={() => document.getElementById('req-file').click()}>
                                <FaFileUpload style={{ fontSize: '1.5rem', marginBottom: '10px' }} />
                                <div>{file ? file.name : "Click to select file (Image/PDF)"}</div>
                                <input
                                    id="req-file"
                                    type="file"
                                    accept="image/*,application/pdf"
                                    onChange={(e) => setFile(e.target.files[0])}
                                    hidden
                                />
                            </div>
                        </div>

                        <button type="submit" className="btn primary" style={{ width: '100%' }} disabled={uploading}>
                            {uploading ? 'Submitting...' : <><FaPaperPlane /> Submit Request</>}
                        </button>
                    </form>
                )}
            </div>
        </div>
    );
};

export default VerificationRequestModal;
