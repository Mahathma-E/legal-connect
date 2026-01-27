import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { FaPaperPlane, FaFileUpload, FaTimes, FaRobot } from 'react-icons/fa';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChatPage = () => {
    const [messages, setMessages] = useState([{ from: 'system', text: '👋 **Welcome to your dedicated Legal Assistant.** \n\nI can assist you with Indian Law. Upload documents or ask any questions.' }]);
    const [input, setInput] = useState('');
    const [file, setFile] = useState(null);
    const [documentContent, setDocumentContent] = useState('');
    const [isUploading, setIsUploading] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    const handleFileUpload = async (e) => {
        const selectedFile = e.target.files[0];
        if (!selectedFile) return;

        setFile(selectedFile);
        setIsUploading(true);

        try {
            const formData = new FormData();
            formData.append('document', selectedFile);

            const response = await axios.post('/upload-document', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });

            setDocumentContent(response.data.content);
            setMessages(prev => [...prev, {
                from: 'system',
                text: `📄 **Document Uploaded:** ${selectedFile.name}`
            }]);
        } catch (error) {
            console.error('Upload error:', error);
            alert('Failed to upload document.');
            setFile(null);
        } finally {
            setIsUploading(false);
        }
    };

    const removeDocument = () => {
        setFile(null);
        setDocumentContent('');
        setMessages(prev => prev.filter(msg => !msg.text.includes('Document Uploaded')));
    };

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMsg = { from: 'user', text: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        const botMsgIndex = messages.length + 1; // Index where bot msg will be
        // Initialize bot message with empty text
        setMessages(prev => [...prev, { from: 'bot', text: '' }]);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMsg.text,
                    document: documentContent
                }),
            });

            if (!response.body) {
                throw new Error('ReadableStream not supported in this browser.');
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let botText = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                botText += chunk;

                // Update the last message (bot's message) with new chunk
                setMessages(prev => {
                    const newMessages = [...prev];
                    // We assume the bot message is the last one we added
                    const lastMsg = newMessages[newMessages.length - 1];
                    if (lastMsg.from === 'bot') {
                        lastMsg.text = botText;
                    }
                    return newMessages;
                });
            }

        } catch (err) {
            console.error(err)
            setMessages(prev => {
                const newMessages = [...prev];
                const lastMsg = newMessages[newMessages.length - 1];
                if (lastMsg.from === 'bot') {
                    lastMsg.text += '\n\n**Error:** Could not get response.';
                } else {
                    newMessages.push({ from: 'bot', text: '**Error:** Connection failed.' });
                }
                return newMessages;
            });
        }
        setIsLoading(false);
    };

    return (
        <div className="chat-page-container">
            <div className="chat-sidebar glass-card">
                <div className="sidebar-header">
                    <img
                        src="/chatbot-logo.jpg"
                        alt="Legal AI"
                        style={{
                            width: '40px',
                            height: '40px',
                            borderRadius: '50%',
                            marginRight: '10px',
                            objectFit: 'cover'
                        }}
                    />
                    <h3>Legal AI</h3>
                </div>
                <div className="chat-history-placeholder">
                    <p className="muted" style={{ padding: '10px' }}>Recent Chats</p>
                    <div className="history-item active">Current Session</div>
                </div>
            </div>

            <div className="chat-main glass-card">
                <div className="chat-display">
                    {messages.map((m, i) => (
                        <div key={i} className={`chat-message ${m.from}`}>
                            <div className="message-bubble">
                                {m.from === 'bot' || m.from === 'system' ? (
                                    <ReactMarkdown
                                        remarkPlugins={[remarkGfm]}
                                        components={{
                                            h1: ({ node, ...props }) => <h1 style={{ fontSize: '1.4em', borderBottom: '1px solid rgba(255,255,255,0.1)', margin: '10px 0' }} {...props} />,
                                            h2: ({ node, ...props }) => <h2 style={{ fontSize: '1.2em', fontWeight: 'bold', margin: '8px 0' }} {...props} />,
                                            h3: ({ node, ...props }) => <h3 style={{ fontSize: '1.1em', fontWeight: 'bold', color: '#a0aec0', margin: '6px 0' }} {...props} />,
                                            ul: ({ node, ...props }) => <ul style={{ paddingLeft: '20px', margin: '5px 0' }} {...props} />,
                                            li: ({ node, ...props }) => <li style={{ marginBottom: '4px' }} {...props} />,
                                            blockquote: ({ node, ...props }) => <blockquote style={{ borderLeft: '4px solid #007bff', paddingLeft: '10px', fontStyle: 'italic', background: 'rgba(0,0,0,0.05)', borderRadius: '4px' }} {...props} />
                                        }}
                                    >
                                        {m.text}
                                    </ReactMarkdown>
                                ) : (
                                    m.text
                                )}
                            </div>
                        </div>
                    ))}
                    {isLoading && <div className="chat-message bot"><div className="message-bubble typing">Thinking...</div></div>}
                    <div ref={messagesEndRef} />
                </div>

                <div className="chat-input-area">
                    {file && (
                        <div className="file-preview">
                            <span>📎 {file.name}</span>
                            <button onClick={removeDocument} style={{ marginLeft: '10px', background: 'none', border: 'none', color: 'red', cursor: 'pointer' }}><FaTimes /></button>
                        </div>
                    )}
                    <div className="input-wrapper">
                        <label className="icon-btn" title="Upload Document">
                            <FaFileUpload size={20} />
                            <input type="file" onChange={handleFileUpload} accept=".pdf,.txt" style={{ display: 'none' }} />
                        </label>
                        <input
                            className="chat-input-field"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                            placeholder="Ask about Indian Law..."
                        />
                        <button className="send-btn" onClick={sendMessage} disabled={isLoading || !input.trim()}>
                            <FaPaperPlane size={20} />
                        </button>
                    </div>
                </div>
            </div>
        </div >
    );
};

export default ChatPage;
