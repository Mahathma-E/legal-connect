import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FaRobot } from 'react-icons/fa';

const Chatbot = () => {
  const navigate = useNavigate();

  return (
    <div
      className="chatbot-icon glass-card"
      onClick={() => navigate('/ai-assistant')}
      style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        border: '1px solid rgba(255,255,255,0.3)',
        boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
        overflow: 'hidden'
      }}
      title="Open Legal Assistant"
    >
      <img
        src="/chatbot-logo.jpg"
        alt="Legal AI"
        style={{
          width: '100%',
          height: '100%',
          borderRadius: '50%',
          objectFit: 'cover',
          objectPosition: 'center',
          transform: 'scale(5.5)'
        }}
      />
    </div>
  );
};

export default Chatbot;