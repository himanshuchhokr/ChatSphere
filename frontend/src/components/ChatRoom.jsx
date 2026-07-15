import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';

export default function ChatRoom() {
  const { id, slug } = useParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [connectionStatus, setConnectionStatus] = useState('connecting'); // connecting | open | closed
  const [error, setError] = useState('');
  const wsRef = useRef(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    let isMounted = true;

    async function init() {
      try {
        const history = await api.getMessages(id);
        if (isMounted) {
          setMessages(history.map((m) => ({
            type: 'message',
            sender: m.sender,
            message: m.content,
            timestamp: m.created_at,
          })));
        }
      } catch (err) {
        setError(err.message);
      }

      const ws = api.connectToRoom(slug);
      wsRef.current = ws;

      ws.onopen = () => setConnectionStatus('open');
      ws.onclose = () => setConnectionStatus('closed');
      ws.onerror = () => setError('WebSocket connection error');

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setMessages((prev) => [...prev, data]);
      };
    }

    init();

    return () => {
      isMounted = false;
      wsRef.current?.close();
    };
  }, [id, slug]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  function handleSend(e) {
    e.preventDefault();
    if (!input.trim() || wsRef.current?.readyState !== WebSocket.OPEN) return;
    wsRef.current.send(JSON.stringify({ message: input.trim() }));
    setInput('');
  }

  return (
    <div className="chat-room-page">
      <header className="chat-room-header">
        <button className="back-btn" onClick={() => navigate('/')}>← Rooms</button>
        <h2>#{slug}</h2>
        <span className={`status-dot ${connectionStatus}`} title={connectionStatus} />
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="messages-panel">
        {messages.map((m, i) =>
          m.type === 'system' ? (
            <div key={i} className="system-message">{m.message}</div>
          ) : (
            <div key={i} className="chat-message">
              <span className="sender">{m.sender}</span>
              <span className="text">{m.message}</span>
            </div>
          )
        )}
        <div ref={bottomRef} />
      </div>

      <form className="message-input-form" onSubmit={handleSend}>
        <input
          type="text"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={connectionStatus !== 'open'}
        />
        <button type="submit" disabled={connectionStatus !== 'open'}>Send</button>
      </form>
    </div>
  );
}
