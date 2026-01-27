import React, { useState } from 'react';
import axios from 'axios';
import { FaHeart, FaComment, FaFlag, FaEdit, FaTrash, FaSave, FaTimes, FaShare, FaCheckCircle } from 'react-icons/fa';
import { Link } from 'react-router-dom';

const CommentItem = ({ comment, allComments, user, postId, refresh, depth = 0 }) => {
  if (!comment || !comment.id) return null; // Safety check
  if (depth > 20) return null; // Prevent infinite recursion

  const [showReply, setShowReply] = useState(false);
  const [replyContent, setReplyContent] = useState('');

  // Find children
  const children = allComments.filter(c => c.parentId === comment.id);

  // Sort children by timestamp
  children.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  const handleReply = async (e) => {
    e.preventDefault();
    if (!replyContent.trim()) return;
    try {
      await axios.post(`/posts/${postId}/comment`, {
        userId: user.id,
        content: replyContent,
        parentId: comment.id,
        timestamp: new Date().toISOString()
      });
      setReplyContent('');
      setShowReply(false);
      refresh();
    } catch (err) {
      alert("Failed to reply");
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Delete this comment?')) return;
    try {
      await axios.delete(`/posts/${postId}/comments/${comment.id}`, { data: { userId: user.id } });
      refresh();
    } catch (err) {
      alert("Failed to delete comment");
    }
  };

  const isOwner = user?.id === comment.userId;
  const isAdmin = user?.role === 'admin';
  // Allow if owner OR post owner (needs passed down) OR admin. For now check owner/admin.

  return (
    <div style={{ marginTop: '10px', paddingLeft: depth > 0 ? '15px' : '0', borderLeft: depth > 0 ? '2px solid rgba(255,255,255,0.1)' : 'none' }}>
      <div style={{ display: 'flex', gap: '10px' }}>
        <Link to={`/profile/${comment.userId}`}>
          <img
            src={comment.userAvatar || '/default-avatar.png'}
            alt="avatar"
            style={{ width: '32px', height: '32px', borderRadius: '50%', objectFit: 'cover' }}
          />
        </Link>
        <div style={{ flex: 1 }}>
          <div style={{ background: 'rgba(255,255,255,0.05)', padding: '10px', borderRadius: '12px', display: 'inline-block', minWidth: '200px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px', marginBottom: '4px' }}>
              <Link to={`/profile/${comment.userId}`} style={{ fontWeight: 'bold', fontSize: '0.9rem', color: 'var(--color-primary)' }}>
                {comment.userName || 'User'}
              </Link>
              {comment.userVerified && <FaCheckCircle style={{ color: 'var(--color-primary)', fontSize: '0.7rem' }} />}
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                {new Date(comment.timestamp).toLocaleDateString()}
              </span>
            </div>
            <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.95rem' }}>{comment.content}</div>
          </div>

          <div style={{ display: 'flex', gap: '15px', marginTop: '5px', fontSize: '0.8rem', marginLeft: '5px' }}>
            <button
              onClick={() => setShowReply(!showReply)}
              style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontWeight: 'bold' }}
            >
              Reply
            </button>
            {(isOwner || isAdmin) && (
              <button
                onClick={handleDelete}
                style={{ background: 'none', border: 'none', color: 'var(--color-danger)', cursor: 'pointer' }}
              >
                Delete
              </button>
            )}
          </div>

          {showReply && (
            <form onSubmit={handleReply} style={{ marginTop: '10px', display: 'flex', gap: '10px' }}>
              <input
                value={replyContent}
                onChange={(e) => setReplyContent(e.target.value)}
                placeholder={`Reply to ${comment.userName}...`}
                style={{ fontSize: '0.9rem', padding: '8px' }}
                autoFocus
              />
              <button type="submit" className="btn primary" style={{ padding: '5px 15px', fontSize: '0.9rem' }}>Send</button>
            </form>
          )}
        </div>
      </div>

      {/* Recursively render children */}
      {children.map(child => (
        <CommentItem
          key={child.id || Math.random()}
          comment={child}
          allComments={allComments}
          user={user}
          postId={postId}
          refresh={refresh}
          depth={depth + 1}
        />
      ))}
    </div>
  );
};

const Post = ({ post, user, refresh }) => {
  const [comment, setComment] = useState('');
  const [showComments, setShowComments] = useState(false);
  const [reason, setReason] = useState('');
  const [showReport, setShowReport] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(post.content || '');
  const [editMedia, setEditMedia] = useState(post.media || []);
  const [newFiles, setNewFiles] = useState([]);

  // Note: 'isFromFollowed' logic is passed from the feed, but we can also check against user state if needed.
  // We'll use the prop passed or default to local check if useful.
  // For the UI badge, we trust the parent 'isFromFollowed' or local check.
  const isFollowed = post.isFromFollowed || (user?.following?.includes(post.userId));
  const isOwner = user?.id === post.userId;
  const isAdmin = user?.role === 'admin';
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

  const handleReport = async (e) => {
    e.preventDefault();
    await axios.post(`/posts/${post.id}/report`, { userId: user.id, reason, timestamp: new Date().toISOString() });
    setShowReport(false); setReason('');
    alert('Reported');
  };

  const startEdit = () => {
    setEditContent(post.content || '');
    setEditMedia(post.media || []);
    setNewFiles([]);
    setIsEditing(true);
  };

  const cancelEdit = () => {
    setIsEditing(false);
    setEditContent(post.content || '');
  };

  const handleUpload = async (file) => {
    const fd = new FormData();
    fd.append('file', file);
    const { data } = await axios.post('/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
    return data.url;
  };

  const saveEdit = async () => {
    if (!editContent.trim() && editMedia.length === 0 && newFiles.length === 0) return;

    try {
      let uploadedUrls = [];
      if (newFiles.length > 0) {
        for (const file of newFiles) {
          try {
            const url = await handleUpload(file);
            uploadedUrls.push(url);
          } catch (err) {
            console.error("Upload failed", err);
            alert("Failed to upload " + file.name);
            return;
          }
        }
      }

      const finalMedia = [...editMedia, ...uploadedUrls];

      await axios.put(`/posts/${post.id}`, { userId: user.id, content: editContent, media: finalMedia });
      setIsEditing(false);
      refresh();
    } catch (error) {
      console.error("Update failed", error);
      alert("Failed to update post");
    }
  };

  const deletePost = async () => {
    if (!window.confirm('Delete this post? This cannot be undone.')) return;
    await axios.delete(`/posts/${post.id}`, { data: { userId: user.id } });
    refresh();
  };

  // Filter top-level comments (no parentId)
  const rootComments = (post.comments || []).filter(c => !c.parentId);

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

        {(isOwner || isAdmin) && (
          <div style={{ display: 'flex', gap: '5px' }}>
            {!isEditing ? (
              <>
                {isOwner && <button className="icon-btn" onClick={startEdit} title="Edit post"><FaEdit /></button>}
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
            style={{ width: '100%', minHeight: '100px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--color-primary)', color: 'white', padding: '10px' }}
          />

          {/* Edit Media Section */}
          <div style={{ marginTop: '10px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9rem' }}>Media:</label>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '10px' }}>
              {/* Existing Media */}
              {editMedia.map((m, i) => (
                <div key={`exist-${i}`} style={{ position: 'relative', width: '80px', height: '80px' }}>
                  {m.match(/\.mp4|\.webm$/i) ? (
                    <video src={m} style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '5px' }} />
                  ) : (
                    <img src={m} alt="preview" style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '5px' }} />
                  )}
                  <button
                    onClick={() => setEditMedia(prev => prev.filter((_, idx) => idx !== i))}
                    style={{ position: 'absolute', top: -5, right: -5, background: 'red', color: 'white', borderRadius: '50%', border: 'none', width: '20px', height: '20px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  >
                    <FaTimes size={12} />
                  </button>
                </div>
              ))}

              {/* New Files Preview */}
              {newFiles.map((f, i) => (
                <div key={`new-${i}`} style={{ position: 'relative', width: '80px', height: '80px', border: '1px dashed grey', borderRadius: '5px' }}>
                  <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px', overflow: 'hidden', color: '#ccc' }}>
                    {f.type.startsWith('image') ? (
                      <img src={URL.createObjectURL(f)} alt="new" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    ) : (
                      <span>{f.name}</span>
                    )}
                  </div>
                  <button
                    onClick={() => setNewFiles(prev => prev.filter((_, idx) => idx !== i))}
                    style={{ position: 'absolute', top: -5, right: -5, background: 'red', color: 'white', borderRadius: '50%', border: 'none', width: '20px', height: '20px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  >
                    <FaTimes size={12} />
                  </button>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <input
                type="file"
                multiple
                accept="image/*,video/*,application/pdf"
                onChange={(e) => setNewFiles(prev => [...prev, ...Array.from(e.target.files)])}
                style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}
              />
            </div>
          </div>
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

          <div style={{ marginBottom: '20px' }}>
            {rootComments.map((c) => (
              <CommentItem
                key={c.id || Math.random()}
                comment={c}
                allComments={post.comments || []}
                user={user}
                postId={post.id}
                refresh={refresh}
              />
            ))}
          </div>

          <form onSubmit={handleComment} style={{ display: 'flex', gap: '10px', marginTop: '15px', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '15px' }}>
            <img
              src={user?.avatar || '/default-avatar.png'}
              alt="me"
              style={{ width: '32px', height: '32px', borderRadius: '50%', objectFit: 'cover' }}
            />
            <div style={{ flex: 1, display: 'flex', gap: '10px' }}>
              <input
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Write a comment..."
                style={{ marginBottom: 0 }}
              />
              <button type="submit" className="btn primary">Send</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default Post;
