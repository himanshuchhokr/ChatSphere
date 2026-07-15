import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../api/client';

export default function Register() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.register(username, email, password);
      await api.login(username, password);
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>💬 ChatSphere</h1>
        <p className="subtitle">Create a new account</p>
        {error && <div className="error-banner">{error}</div>}
        <input type="text" placeholder="Username" value={username}
          onChange={(e) => setUsername(e.target.value)} required />
        <input type="email" placeholder="Email" value={email}
          onChange={(e) => setEmail(e.target.value)} />
        <input type="password" placeholder="Password" value={password}
          onChange={(e) => setPassword(e.target.value)} required />
        <button type="submit" disabled={loading}>{loading ? 'Creating account...' : 'Register'}</button>
        <p className="switch-link">Already have an account? <Link to="/login">Log In</Link></p>
      </form>
    </div>
  );
}
