import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Post from './Post';
import DM from './DM';
import { FaPlus } from 'react-icons/fa';

const Home = ({ user, showDMs }) => {
  const [content, setContent] = useState('');
  const [media, setMedia] = useState([]);
  const [posts, setPosts] = useState([]);
  const [search, setSearch] = useState('');

  const fetchPosts = async () => {
    const { data } = await axios.get(`/posts?userId=${user.id}`);
    setPosts(data || []);
  };

  useEffect(() => { fetchPosts(); }, []);

  const handleUpload = async (file) => {
    const fd = new FormData();
    fd.append('file', file);
    const { data } = await axios.post('/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
    return data.url;
  };

  const handlePost = async (e) => {
    e.preventDefault();
    try {
      const mediaUrls = [];
      for (const f of media) {
        try {
          mediaUrls.push(await handleUpload(f));
        } catch (err) {
          console.error("Upload failed for file:", f.name, err);
          alert(`Failed to upload ${f.name}. Supported formats: PNG, JPG, GIF, WEBP, MP4, PDF, TXT.`);
          return; // Stop posting if upload fails
        }
      }

      await axios.post('/posts', {
        userId: user.id,
        content,
        media: mediaUrls,
        timestamp: new Date().toISOString()
      });

      setContent('');
      setMedia([]);
      // Reset file input manually if possible, or just rely on state
      document.querySelector('input[type="file"]').value = '';

      fetchPosts();
    } catch (err) {
      console.error("Failed to create post:", err);
      alert("Failed to create post. Please try again.");
    }
  };

  const filtered = posts.filter(p => (p.content || '').toLowerCase().includes(search.toLowerCase()));

  if (showDMs) {
    return (
      <div className="container">
        <DM user={user} />
      </div>
    );
  }

  return (
    <div className="container">
      <div className="glass-card composer">
        <form onSubmit={handlePost}>
          <textarea
            placeholder="What's on your legal mind?"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
            style={{ minHeight: '100px', fontSize: '1.1rem' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px' }}>
            <label htmlFor="file-upload" className="btn secondary link-btn" style={{ cursor: 'pointer', borderRadius: '50%', width: '40px', height: '40px', padding: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }} title="Add Media">
              <FaPlus />
            </label>
            <input
              id="file-upload"
              type="file"
              multiple
              onChange={(e) => setMedia(Array.from(e.target.files))}
              accept="image/*,video/*,application/pdf"
              style={{ display: 'none' }}
            />
            {media.length > 0 && <span style={{ fontSize: '0.8rem', marginLeft: '10px', color: 'var(--text-muted)' }}>{media.length} selected</span>}
            <button type="submit" className="btn primary">Post Update</button>
          </div>
        </form>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Search posts..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ padding: '15px' }}
        />
      </div>

      <div className="feed">
        {filtered.map(post => (
          <Post key={post.id} post={post} user={user} refresh={fetchPosts} />
        ))}
        {filtered.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            <p>No posts found.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
