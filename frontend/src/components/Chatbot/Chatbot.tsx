import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './Chatbot.css';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  products?: Product[];
  suggestions?: string[];
}

interface Product {
  id: string;
  name: string;
  price: number;
  image_url?: string;
  description?: string;
  in_stock?: boolean;
  stock_quantity?: number;
  allergens?: string[];
}

interface ChatbotResponse {
  type: string;
  message: string;
  products?: Product[];
  suggestions?: string[];
}

const Chatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [imageError, setImageError] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fallback avatar if image doesn't load
  const avatarFallback = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='45' fill='%23ff6b35'/%3E%3Ctext x='50' y='65' font-size='50' text-anchor='middle' fill='white'%3E👨‍🍳%3C/text%3E%3C/svg%3E";

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      // Send initial greeting
      sendMessage('hi');
    }
  }, [isOpen]);

  const sendMessage = async (message: string) => {
    if (!message.trim() && message !== 'hi') return;

    // Add user message (skip for initial greeting)
    if (message !== 'hi') {
      const userMessage: Message = {
        id: Date.now().toString(),
        type: 'user',
        content: message,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, userMessage]);
    }

    setInputValue('');
    setIsLoading(true);

    try {
      const response = await axios.post<ChatbotResponse>(
        'http://localhost:5000/api/v1/chatbot/message',
        { message }
      );

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: response.data.message,
        timestamp: new Date(),
        products: response.data.products,
        suggestions: response.data.suggestions
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chatbot error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: 'Oops! Something went wrong. Please try again! 😅',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      sendMessage(inputValue);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion);
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <>
      {/* Floating Button */}
      <div
        className={`chatbot-button ${isOpen ? 'chatbot-button-hidden' : ''}`}
        onClick={toggleChat}
      >
        <img
          src={imageError ? avatarFallback : "/chef-cookie.svg"}
          alt="Chef Cookie Assistant"
          className="chatbot-avatar"
          onError={() => setImageError(true)}
        />
        <div className="chatbot-button-pulse"></div>
      </div>

      {/* Chat Window */}
      {isOpen && (
        <div className="chatbot-window">
          {/* Header */}
          <div className="chatbot-header">
            <div className="chatbot-header-content">
              <img
                src={imageError ? avatarFallback : "/chef-cookie.svg"}
                alt="Chef Cookie"
                className="chatbot-header-avatar"
                onError={() => setImageError(true)}
              />
              <div className="chatbot-header-text">
                <h3>Chef Cookie</h3>
                <p className="chatbot-status">
                  <span className="chatbot-status-dot"></span>
                  Online
                </p>
              </div>
            </div>
            <button
              className="chatbot-close-btn"
              onClick={toggleChat}
              aria-label="Close chat"
            >
              ×
            </button>
          </div>

          {/* Messages */}
          <div className="chatbot-messages">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`chatbot-message ${message.type === 'user' ? 'chatbot-message-user' : 'chatbot-message-bot'}`}
              >
                {message.type === 'bot' && (
                  <img
                    src={imageError ? avatarFallback : "/chef-cookie.svg"}
                    alt="Chef Cookie"
                    className="chatbot-message-avatar"
                    onError={() => setImageError(true)}
                  />
                )}
                <div className="chatbot-message-content">
                  <div className="chatbot-message-bubble">
                    <p className="chatbot-message-text">{message.content}</p>

                    {/* Products Grid */}
                    {message.products && message.products.length > 0 && (
                      <div className="chatbot-products-grid">
                        {message.products.map((product) => (
                          <div key={product.id} className="chatbot-product-card">
                            {product.image_url && (
                              <img
                                src={product.image_url}
                                alt={product.name}
                                className="chatbot-product-image"
                              />
                            )}
                            <div className="chatbot-product-info">
                              <h4>{product.name}</h4>
                              <p className="chatbot-product-price">₹{product.price.toFixed(2)}</p>
                              {product.in_stock !== undefined && (
                                <span className={`chatbot-product-stock ${product.in_stock ? 'in-stock' : 'out-of-stock'}`}>
                                  {product.in_stock ? '✓ In Stock' : '✗ Out of Stock'}
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Suggestions */}
                  {message.suggestions && message.suggestions.length > 0 && (
                    <div className="chatbot-suggestions">
                      {message.suggestions.map((suggestion, index) => (
                        <button
                          key={index}
                          className="chatbot-suggestion-btn"
                          onClick={() => handleSuggestionClick(suggestion)}
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}

                  <span className="chatbot-message-time">{formatTime(message.timestamp)}</span>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="chatbot-message chatbot-message-bot">
                <img
                  src={imageError ? avatarFallback : "/chef-cookie.svg"}
                  alt="Chef Cookie"
                  className="chatbot-message-avatar"
                  onError={() => setImageError(true)}
                />
                <div className="chatbot-message-content">
                  <div className="chatbot-message-bubble">
                    <div className="chatbot-typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form className="chatbot-input-form" onSubmit={handleSubmit}>
            <input
              type="text"
              className="chatbot-input"
              placeholder="Ask me anything about cookies..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isLoading}
            />
            <button
              type="submit"
              className="chatbot-send-btn"
              disabled={isLoading || !inputValue.trim()}
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </form>
        </div>
      )}
    </>
  );
};

export default Chatbot;
