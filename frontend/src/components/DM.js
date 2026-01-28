import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './DM.css'; // Import the new CSS file
import { FaPaperPlane, FaArrowLeft, FaSearch, FaComments } from 'react-icons/fa'; // Import icons

const DM = ({ user }) => {
  const { convId } = useParams();
  const navigate = useNavigate();
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
    const interval = setInterval(fetchConversations, 5000);
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
      setSearchTerm('');
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

  const handleBack = () => {
    setCurrentConvId(null);
    setConv(null);
  };

  const getOtherUser = (c) => {
    if (!c || !c.users) return null;
    return allUsers.find(u => u.id === c.users.find(uid => uid !== user.id));
  };

  const activeChatUser = conv ? getOtherUser(conv) : null;

  return (
    <div className={`dm-container ${currentConvId ? 'active-chat' : ''}`}>
      {/* Sidebar - User List & Search */}
      <div className="dm-sidebar">
        <div className="dm-sidebar-header">
          <h2>Messages</h2>
          <input
            type="text"
            placeholder="Search users..."
            className="dm-search-bar"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="dm-list">
          {searchTerm && (
            <>
              <div className="dm-section-title">Search Results</div>
              {filteredUsers.length === 0 && <p className="dm-status" style={{ padding: '0 20px' }}>No users found.</p>}
              {filteredUsers.map(u => (
                <div key={u.id} className="dm-item" onClick={() => startConversation(u.id)}>
                  <img src={u.avatar} alt="avatar" className="dm-avatar" />
                  <div className="dm-info">
                    <span className="dm-name">{u.name}</span>
                    <span className="dm-status">Start a conversation</span>
                  </div>
                </div>
              ))}
            </>
          )}

          <div className="dm-section-title">Recent Conversations</div>
          {conversations.length === 0 && <p className="dm-status" style={{ padding: '0 20px' }}>No conversations yet.</p>}
          {conversations.map(c => {
            const otherUser = getOtherUser(c);
            return (
              <div
                key={c.id}
                className={`dm-item ${currentConvId === c.id ? 'active' : ''}`}
                onClick={() => handleConversationClick(c)}
              >
                <img src={otherUser?.avatar || '/default-avatar.png'} alt="avatar" className="dm-avatar" />
                <div className="dm-info">
                  <span className="dm-name">{otherUser?.name || 'Unknown User'}</span>
                  <span className="dm-status">
                    {c.messages && c.messages.length > 0
                      ? c.messages[c.messages.length - 1].content.substring(0, 25) + (c.messages[c.messages.length - 1].content.length > 25 ? '...' : '')
                      : 'Start chatting'}
                  </span>
                </div>
                {c.status === 'pending' && <span className="badge">Pending</span>}
              </div>
            );
          })}
        </div>
      </div>

      {/* Chat Area - Helper logic handles empty state vs chat */}
      <div className="dm-chat-area">
        {!currentConvId ? (
          <div className="dm-empty-state">
            <div className="dm-empty-icon"><FaComments /></div>
            <h3>Select a conversation</h3>
            <p>Choose a user from the left to start chatting.</p>
          </div>
        ) : (
          <>
            <div className="dm-chat-header">
              <button onClick={handleBack} className="dm-back-btn"><FaArrowLeft /></button>
              {activeChatUser && (
                <>
                  <img src={activeChatUser.avatar || '/default-avatar.png'} alt="avatar" className="dm-avatar" style={{ width: '40px', height: '40px' }} />
                  <div>
                    <div className="dm-name">{activeChatUser.name}</div>
                    <div className="dm-status" style={{ fontSize: '0.75rem' }}>Online</div>
                  </div>
                </>
              )}
            </div>

            <div className="dm-messages-container">
              {messages.map((m, i) => (
                <div key={i} className={`message-row ${m.from === user.id ? 'sent' : 'received'}`}>
                  {m.from !== user.id && (
                    <img src={activeChatUser?.avatar || '/default-avatar.png'} alt="avatar" className="dm-avatar" style={{ width: '32px', height: '32px', alignSelf: 'flex-end' }} />
                  )}
                  <div>
                    <div className="message-bubble">{m.content}</div>
                    <div className="message-time">{new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                  </div>
                </div>
              ))}
              <div ref={bottomRef} />
            </div>

            <form onSubmit={send} className="dm-composer">
              <input
                className="dm-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message..."
              />
              <button className="dm-send-btn" type="submit"><FaPaperPlane /></button>
            </form>
          </>
        )}
      </div>
    </div>
  );
};

export default DM;
