import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaSearch, FaBook, FaSortAlphaDown } from 'react-icons/fa';

const Constitution = () => {
    const [data, setData] = useState({ parts: [] });
    const [search, setSearch] = useState('');
    const [selectedPart, setSelectedPart] = useState('ALL');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await axios.get('/constitution');
                setData(res.data);
            } catch (err) {
                console.error("Error fetching constitution:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const getFilteredArticles = () => {
        let articles = [];
        data.parts.forEach(part => {
            if (selectedPart === 'ALL' || selectedPart === part.id) {
                part.articles.forEach(art => {
                    if (
                        art.content.toLowerCase().includes(search.toLowerCase()) ||
                        art.title.toLowerCase().includes(search.toLowerCase()) ||
                        art.id.toLowerCase().includes(search.toLowerCase())
                    ) {
                        articles.push({ ...art, partTitle: part.title });
                    }
                });
            }
        });
        return articles;
    };

    const filteredArticles = getFilteredArticles();

    return (
        <div className="container" style={{ display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
            {/* Sidebar - Parts List */}
            <div className="glass-card" style={{ width: '250px', position: 'sticky', top: '100px', maxHeight: '80vh', overflowY: 'auto' }}>
                <h3 style={{ marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FaBook /> Parts
                </h3>
                <div
                    className={`nav-item ${selectedPart === 'ALL' ? 'active' : ''}`}
                    onClick={() => setSelectedPart('ALL')}
                    style={{ padding: '10px', cursor: 'pointer', borderRadius: '8px', marginBottom: '5px', background: selectedPart === 'ALL' ? 'var(--color-primary)' : 'transparent' }}
                >
                    All Articles
                </div>
                {data.parts.map(part => (
                    <div
                        key={part.id}
                        className={`nav-item ${selectedPart === part.id ? 'active' : ''}`}
                        onClick={() => setSelectedPart(part.id)}
                        style={{ padding: '10px', cursor: 'pointer', borderRadius: '8px', marginBottom: '5px', fontSize: '0.9rem', background: selectedPart === part.id ? 'rgba(255,255,255,0.1)' : 'transparent' }}
                    >
                        {part.title}
                    </div>
                ))}
            </div>

            {/* Main Content */}
            <div style={{ flex: 1 }}>
                <div className="glass-card" style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <FaSearch className="muted" />
                    <input
                        type="text"
                        placeholder="Search articles, keywords..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        style={{ marginBottom: 0, background: 'transparent', border: 'none', padding: '5px' }}
                    />
                </div>

                {loading ? (
                    <div style={{ textAlign: 'center', padding: '50px' }}>Loading Constitution...</div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                        {filteredArticles.length === 0 && (
                            <div className="glass-card" style={{ textAlign: 'center', padding: '40px' }}>
                                <p>No articles found matching "{search}"</p>
                            </div>
                        )}
                        {filteredArticles.map((art, i) => (
                            <div key={i} className="glass-card">
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                                    <span style={{ fontSize: '0.8rem', color: 'var(--color-primary)', fontWeight: 'bold' }}>{art.partTitle}</span>
                                    <span style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>Article {art.id}</span>
                                </div>
                                <h3 style={{ marginBottom: '10px' }}>{art.title}</h3>
                                <p style={{ lineHeight: '1.6', whiteSpace: 'pre-wrap', color: 'var(--text-main)' }}>{art.content}</p>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Constitution;
