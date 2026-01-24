import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaSearch, FaBook, FaChevronDown, FaChevronRight, FaScroll } from 'react-icons/fa';

const Constitution = () => {
    const [data, setData] = useState({ parts: [] });
    const [selectedArticle, setSelectedArticle] = useState(null);
    const [expandedParts, setExpandedParts] = useState(['PREAMBLE']);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [isSearching, setIsSearching] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await axios.get('/constitution');
                setData(res.data);
                // Auto-select Preamble on load
                if (res.data.parts.length > 0 && res.data.parts[0].articles.length > 0) {
                    setSelectedArticle({
                        ...res.data.parts[0].articles[0],
                        partTitle: res.data.parts[0].title,
                        partId: res.data.parts[0].id
                    });
                }
            } catch (err) {
                console.error("Error fetching constitution:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    // Handle search
    useEffect(() => {
        if (searchQuery.trim() === '') {
            setIsSearching(false);
            setSearchResults([]);
            return;
        }

        setIsSearching(true);
        const query = searchQuery.toLowerCase();
        const results = [];

        data.parts.forEach(part => {
            part.articles.forEach(article => {
                const articleNum = article.id.toLowerCase();
                const title = article.title.toLowerCase();
                const content = article.content.toLowerCase();

                // Match article number (e.g., "21", "article 21", "art 21")
                const numMatch = query.match(/(?:article|art\.?)\s*(\d+[a-z]?)/i) || query.match(/^(\d+[a-z]?)$/);
                const searchNum = numMatch ? numMatch[1] : query;

                if (articleNum.includes(searchNum) || 
                    title.includes(query) || 
                    content.includes(query)) {
                    results.push({
                        ...article,
                        partTitle: part.title,
                        partId: part.id
                    });
                }
            });
        });

        setSearchResults(results);
    }, [searchQuery, data]);

    const togglePart = (partId) => {
        setExpandedParts(prev => 
            prev.includes(partId) 
                ? prev.filter(id => id !== partId)
                : [...prev, partId]
        );
    };

    const selectArticle = (article, partTitle, partId) => {
        setSelectedArticle({ ...article, partTitle, partId });
        setSearchQuery(''); // Clear search when selecting an article
    };

    const cleanText = (text) => {
        if (!text) return '';
        // Remove corrupted encoding characters
        return text.replace(/[\u00a3\u00c9\u00aa\u00ba\u00c6\u00ca\u00b4]/g, '');
    };

    const getPreview = (content, maxLength = 150) => {
        const cleaned = cleanText(content);
        if (cleaned.length <= maxLength) return cleaned;
        return cleaned.substring(0, maxLength) + '...';
    };

    if (loading) {
        return (
            <div className="container" style={{ textAlign: 'center', padding: '50px' }}>
                <FaBook size={40} style={{ marginBottom: '20px', color: 'var(--color-primary)' }} />
                <p>Loading Constitution of India...</p>
            </div>
        );
    }

    return (
        <div className="constitution-container">
            {/* Search Bar - Top */}
            <div className="constitution-search-bar glass-card">
                <FaSearch className="search-icon" />
                <input
                    type="text"
                    placeholder="Search by article number, title, or keywords..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="constitution-search-input"
                />
                {searchQuery && (
                    <button 
                        className="clear-search-btn"
                        onClick={() => setSearchQuery('')}
                        aria-label="Clear search"
                    >
                        ✕
                    </button>
                )}
            </div>

            <div className="constitution-main-layout">
                {/* Sidebar - Left */}
                <aside className="constitution-sidebar glass-card">
                    <div className="sidebar-header">
                        <FaScroll size={20} />
                        <h3>Constitution of India</h3>
                    </div>
                    <div className="parts-list">
                        {data.parts.map(part => (
                            <div key={part.id} className="part-item">
                                <div 
                                    className="part-header"
                                    onClick={() => togglePart(part.id)}
                                >
                                    {expandedParts.includes(part.id) ? 
                                        <FaChevronDown className="chevron" /> : 
                                        <FaChevronRight className="chevron" />
                                    }
                                    <span className="part-title">{part.title}</span>
                                    <span className="article-count">{part.articles.length}</span>
                                </div>
                                {expandedParts.includes(part.id) && (
                                    <div className="articles-list">
                                        {part.articles.map(article => (
                                            <div
                                                key={article.id}
                                                className={`article-item ${
                                                    selectedArticle?.id === article.id && 
                                                    selectedArticle?.partId === part.id ? 'active' : ''
                                                }`}
                                                onClick={() => selectArticle(article, part.title, part.id)}
                                            >
                                                <span className="article-number">
                                                    {article.id === 'PREAMBLE' ? 'Preamble' : `Article ${article.id}`}
                                                </span>
                                                <span className="article-title-preview">
                                                    {article.title.substring(0, 40)}
                                                    {article.title.length > 40 ? '...' : ''}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </aside>

                {/* Main Content - Center */}
                <main className="constitution-content">
                    {isSearching ? (
                        // Search Results View
                        <div className="search-results">
                            <h2 className="search-results-header">
                                Search Results ({searchResults.length})
                            </h2>
                            {searchResults.length === 0 ? (
                                <div className="no-results glass-card">
                                    <p>No articles found matching "{searchQuery}"</p>
                                    <p className="muted">Try searching by article number, title, or keywords</p>
                                </div>
                            ) : (
                                <div className="search-results-grid">
                                    {searchResults.map((article, idx) => (
                                        <div key={idx} className="search-result-card glass-card">
                                            <div className="result-header">
                                                <span className="result-part-badge">{article.partTitle}</span>
                                                <span className="result-article-number">
                                                    {article.id === 'PREAMBLE' ? 'Preamble' : `Article ${article.id}`}
                                                </span>
                                            </div>
                                            <h3 className="result-title">{cleanText(article.title)}</h3>
                                            <p className="result-preview">
                                                {getPreview(article.content)}
                                            </p>
                                            <button
                                                className="btn primary view-article-btn"
                                                onClick={() => selectArticle(article, article.partTitle, article.partId)}
                                            >
                                                View Full Article
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ) : (
                        // Article Viewer
                        selectedArticle ? (
                            <div className="article-viewer glass-card">
                                <div className="article-header">
                                    <span className="article-part-badge">{selectedArticle.partTitle}</span>
                                    <h1 className="article-number">
                                        {selectedArticle.id === 'PREAMBLE' ? 'Preamble' : `Article ${selectedArticle.id}`}
                                    </h1>
                                    <h2 className="article-title">{cleanText(selectedArticle.title)}</h2>
                                </div>

                                <div className="article-body">
                                    <div className="article-section">
                                        <h3 className="section-title">
                                            <FaBook style={{ marginRight: '8px' }} />
                                            Original Text
                                        </h3>
                                        <div className="section-content">
                                            {cleanText(selectedArticle.content) || (
                                                <p className="muted">No content available for this article.</p>
                                            )}
                                        </div>
                                    </div>

                                    {selectedArticle.simpleExplanation && (
                                        <div className="article-section">
                                            <h3 className="section-title">
                                                💡 Simple Explanation
                                            </h3>
                                            <div className="section-content explanation">
                                                {cleanText(selectedArticle.simpleExplanation)}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ) : (
                            <div className="no-selection glass-card">
                                <FaBook size={60} style={{ color: 'var(--color-primary)', marginBottom: '20px' }} />
                                <h2>Welcome to the Constitution of India</h2>
                                <p className="muted">Select an article from the sidebar to begin reading</p>
                            </div>
                        )
                    )}
                </main>
            </div>
        </div>
    );
};

export default Constitution;
