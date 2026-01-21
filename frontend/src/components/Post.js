import React, { useState } from 'react';
import axios from 'axios';
import { FaHeart, FaComment, FaFlag, FaEdit, FaTrash, FaSave, FaTimes, FaShare, FaCheckCircle } from 'react-icons/fa';
import { Link } from 'react-router-dom';

const Post = ({ post, user, refresh }) => {
  const [comment, setComment] = useState('');
  const [showComments, setShowComments] = useState(false);
  const [reason, setReason] = useState('');
  const [showReport, setShowReport] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(post.content || '');

  // Note: 'isFromFollowed' logic is passed from the feed, but we can also check against user state if needed.
  // We'll use the prop passed or default to local check if useful.
  // For the UI badge, we trust the parent 'isFromFollowed' or local check.
  const isFollowed = post.isFromFollowed || (user?.following?.includes(post.userId));
  const isOwner = user?.id === post.userId;
  const isVerified = post.user?.isVerified && post.user?.role === 'lawyer';

  const handleLike = async () => {
    await axios.post(`/posts/${post.id}/like`, { userId: user.id });
    refresh();
  };

  const handleComment = async (e) => {
    e.preventDefault();
    if (!comment.trim()) return;
    await axios.post(`/posts/${post.id}/comment`, { userId: user.id, content: comment, timestamp: new Date().toISOString() });
    setComment(''); setShowComments(true);
    refresh();
  };

  const handleDeleteComment = async (commentIndex) => {
    if (!window.confirm('Delete this comment?')) return;
    await axios.delete(`/posts/${post.id}/comments/${commentIndex}`, { data: { userId: user.id } });
    refresh();
  };

  const handleReport = async (e) => {
    e.preventDefault();
    await axios.post(`/posts/${post.id}/report`, { userId: user.id, reason, timestamp: new Date().toISOString() });
    setShowReport(false); setReason('');
    alert('Reported');
  };

  const startEdit = () => {
    setEditContent(post.content || '');
    setIsEditing(true);
  };

  const cancelEdit = () => {
    setIsEditing(false);
    setEditContent(post.content || '');
  };

  const saveEdit = async () => {
    if (!editContent.trim()) return;
    await axios.put(`/posts/${post.id}`, { userId: user.id, content: editContent });
    setIsEditing(false);
    refresh();
  };

  const deletePost = async () => {
    if (!window.confirm('Delete this post? This cannot be undone.')) return;
    await axios.delete(`/posts/${post.id}`, { data: { userId: user.id } });
    refresh();
  };

  return (
    <div className="glass-card post">
      <div className="post-header">
        <div className="user-info">
          <Link to={`/profile/${post.userId}`}>
            <img src={post.user?.avatar || '/default-avatar.png'} alt="avatar" className="avatar-sm" />
          </Link>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
              <Link to={`/profile/${post.userId}`} style={{ fontWeight: '600' }}>
                {post.user?.name || 'Unknown User'}
              </Link>
              {isVerified && <FaCheckCircle style={{ color: 'var(--color-primary)', fontSize: '0.8rem' }} title="Verified User" />}
              {isFollowed && <span className="followed-badge">Following</span>}
            </div>
            <div className="muted" style={{ fontSize: '0.8rem' }}>
              {new Date(post.timestamp).toLocaleString()}
              {post.updatedAt && <span> • Edited</span>}
            </div>
          </div>
        </div>

        {isOwner && (
          <div style={{ display: 'flex', gap: '5px' }}>
            {!isEditing ? (
              <>
                <button className="icon-btn" onClick={startEdit} title="Edit post"><FaEdit /></button>
                <button className="icon-btn danger" style={{ color: 'var(--color-danger)' }} onClick={deletePost} title="Delete post"><FaTrash /></button>
              </>
            ) : (
              <>
                <button className="icon-btn success" style={{ color: 'var(--color-success)' }} onClick={saveEdit} title="Save"><FaSave /></button>
                <button className="icon-btn" onClick={cancelEdit} title="Cancel"><FaTimes /></button>
              </>
            )}
          </div>
        )}
      </div>

      {!isEditing ? (
        <div style={{ fontSize: '1rem', lineHeight: '1.5', whiteSpace: 'pre-wrap', marginBottom: '15px' }}>
          {post.content}
        </div>
      ) : (
        <div style={{ marginBottom: '15px' }}>
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            style={{ width: '100%', minHeight: '100px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--color-primary)' }}
          />
        </div>
      )}

      {post.media && post.media.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px', marginBottom: '15px' }}>
          {post.media.map((m, i) => (
            <div key={i} style={{ borderRadius: 'var(--radius-sm)', overflow: 'hidden' }}>
              {m.match(/\.mp4|\.webm$/i) ? (
                <video src={m} controls style={{ width: '100%', display: 'block' }} />
              ) : (
                <img src={m} alt={`media-${i}`} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              )}
            </div>
          ))}
        </div>
      )}

      <div className="post-actions">
        <button
          className={`action-btn ${post.likes?.includes(user?.id) ? 'active' : ''}`}
          onClick={handleLike}
        >
          <FaHeart /> {post.likes?.length || 0}
        </button>
        <button className="action-btn" onClick={() => setShowComments(v => !v)}>
          <FaComment /> {post.comments?.length || 0}
        </button>
        <button className="action-btn" onClick={() => setShowReport(v => !v)} style={{ marginLeft: 'auto' }}>
          <FaFlag /> Report
        </button>
      </div>

      {showReport && (
        <form onSubmit={handleReport} style={{ marginTop: '15px', display: 'flex', gap: '10px' }}>
          <input
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Reason for report..."
            required
            style={{ marginBottom: 0 }}
          />
          <button type="submit" className="btn danger" style={{ whiteSpace: 'nowrap' }}>Submit</button>
        </form>
      )}

      {showComments && (
        <div className="comments-section">
          {(!post.comments || post.comments.length === 0) && (
            <p className="muted" style={{ textAlign: 'center', marginBottom: '15px' }}>No comments yet. Be the first!</p>
          )}

          {(post.comments || []).map((c, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px', paddingBottom: '10px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
              <div>
                <strong style={{ color: 'var(--color-primary)', marginRight: '5px' }}>{c.userName || 'User'}:</strong>
                <span style={{ color: 'var(--text-main)' }}>{c.content}</span>
              </div>
              {user?.id === c.userId && (
                <button
                  onClick={() => handleDeleteComment(i)}
                  style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                  title="Delete"
                >
                  <FaTrash />
                </button>
              )}
            </div>
          ))}

          <form onSubmit={handleComment} style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
            <input
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Write a comment..."
              style={{ marginBottom: 0 }}
            />
            <button type="submit" className="btn primary">Send</button>
          </form>
        </div>
      )}
    </div>
  );
};

export default Post;
