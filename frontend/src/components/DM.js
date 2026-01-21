import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const DM = ({ user }) => {
  const { convId } = useParams(); // This will be used if we navigate directly to a DM
  const [currentConvId, setCurrentConvId] = useState(convId);
  const [conv, setConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [allUsers, setAllUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [conversations, setConversations] = useState([]);
  const bottomRef = useRef(null);

  // Fetch all users
  useEffect(() => {
    const fetchAllUsers = async () => {
      try {
        const { data } = await axios.get('/users');
        // Filter out the current user
        setAllUsers(data.filter(u => u.id !== user.id));
      } catch (err) {
        console.error("Error fetching users:", err);
      }
    };
    fetchAllUsers();
  }, [user.id]);

  // Filter users based on search term
  useEffect(() => {
    setFilteredUsers(
      allUsers.filter(u => u.name.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  }, [searchTerm, allUsers]);

  // Fetch conversations
  const fetchConversations = async () => {
    try {
      const { data } = await axios.get(`/conversations?userId=${user.id}`);
      setConversations(data || []);
    } catch (err) {
      console.error("Error fetching conversations:", err);
    }
  };

  useEffect(() => {
    fetchConversations();
    const interval = setInterval(fetchConversations, 5000); // Poll for new conversations
    return () => clearInterval(interval);
  }, [user.id]);

  // Fetch current conversation messages
  const fetchCurrentConv = async () => {
    if (!currentConvId) return;
    try {
      const { data } = await axios.get(`/conversations/${currentConvId}`);
      setConv(data);
      setMessages(data.messages || []);
    } catch (err) {
      console.error(err);
      setConv(null);
      setMessages([]);
    }
  };

  useEffect(() => {
    fetchCurrentConv();
    const interval = setInterval(fetchCurrentConv, 3000);
    return () => clearInterval(interval);
  }, [currentConvId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startConversation = async (targetUserId) => {
    try {
      const { data } = await axios.post('/conversations', {
        users: [user.id, targetUserId]
      });
      setCurrentConvId(data.id);
      setConv(data);
      setMessages(data.messages || []);
      setSearchTerm(''); // Clear search after starting conversation
    } catch (err) {
      console.error("Error starting conversation:", err);
      if (err.response?.status === 403) {
        alert("You must follow this user to send them a DM. Visit their profile and click Follow first.");
      } else {
        alert("Could not start conversation. Please try again.");
      }
    }
  };

  const send = async (e) => {
    e.preventDefault();
    if (!input.trim() || !currentConvId) return;
    try {
      await axios.post(`/conversations/${currentConvId}/message`, {
        from: user.id,
        content: input,
        timestamp: new Date().toISOString()
      });
      setInput('');
      fetchCurrentConv();
    } catch (err) {
      console.error(err);
    }
  };

  const handleConversationClick = (c) => {
    setCurrentConvId(c.id);
    setConv(c);
    setMessages(c.messages || []);
  };

  return (
    <div className="container dm-page">
      {!currentConvId ? (
        <div className="dm-list-panel">
          <h2>Direct Messages</h2>
          <input
            type="text"
            placeholder="Search users to start a DM..."
            className="search-wide"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {searchTerm && (
            <div className="user-search-results">
              {filteredUsers.length === 0 && <p>No users found.</p>}
              {filteredUsers.map(u => (
                <div key={u.id} className="user-item" onClick={() => startConversation(u.id)}>
                  <img src={u.avatar} alt="avatar" className="avatar-sm" />
                  <span>{u.name}</span>
                </div>
              ))}
            </div>
          )}
          
          <h3>Your Conversations</h3>
          <div className="conversation-list">
            {conversations.length === 0 && <p>No conversations yet.</p>}
            {conversations.map(c => {
              const otherUser = allUsers.find(u => u.id === c.users.find(uid => uid !== user.id));
              return (
                <div key={c.id} className="conversation-item" onClick={() => handleConversationClick(c)}>
                  <img src={otherUser?.avatar || '/default-avatar.png'} alt="avatar" className="avatar-sm" />
                  <span>{otherUser?.name || 'Unknown User'}</span>
                  {c.status === 'pending' && <span className="badge">Pending</span>}
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="dm-thread-panel">
          <button onClick={() => setCurrentConvId(null)} className="btn secondary back-button">Back to DMs</button>
          {conv ? (
            <>
              <h2>Direct Messages with {conv.participants?.find(p => p.id !== user.id)?.name || allUsers.find(u => u.id === conv.users.find(uid => uid !== user.id))?.name || 'Loading...'}</h2>
              <div className="dm-thread">
                {messages.map((m, i) => {
                  const sender = allUsers.find(u => u.id === m.from) || user;
                  return (
                    <div key={i} className={`dm-msg ${m.from === user.id ? 'me' : 'them'}`}>
                      <img
                        src={sender.avatar || '/default-avatar.png'}
                        alt="avatar"
                        className="avatar-sm"
                      />
                      <div className="bubble">{m.content}</div>
                      <div className="time">{new Date(m.timestamp).toLocaleTimeString()}</div>
                    </div>
                  );
                })}
                <div ref={bottomRef} />
              </div>
              <form onSubmit={send} className="dm-composer">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Type your message…"
                />
                <button className="btn primary" type="submit">Send</button>
              </form>
            </>
          ) : (
            <p>Loading conversation...</p>
          )}
        </div>
      )}
    </div>
  );
};

export default DM;
