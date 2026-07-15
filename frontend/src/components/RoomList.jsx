import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';

export default function RoomList() {
  const [rooms, setRooms] = useState([]);
  const [newRoomName, setNewRoomName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  async function loadRooms() {
    setLoading(true);
    try {
      const data = await api.getRooms();
      setRooms(data.results ?? data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRooms();
  }, []);

  async function handleCreateRoom(e) {
    e.preventDefault();
    if (!newRoomName.trim()) return;
    try {
      const room = await api.createRoom(newRoomName.trim());
      setNewRoomName('');
      navigate(`/room/${room.id}/${room.slug}`);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleJoinAndEnter(room) {
    try {
      await api.joinRoom(room.id);
      navigate(`/room/${room.id}/${room.slug}`);
    } catch (err) {
      setError(err.message);
    }
  }

  function handleLogout() {
    api.logout();
    navigate('/login');
  }

  return (
    <div className="room-list-page">
      <header className="dashboard-header">
        <h1>💬 ChatSphere</h1>
        <button className="logout-btn" onClick={handleLogout}>Log Out</button>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <form className="create-room-form" onSubmit={handleCreateRoom}>
        <input
          type="text"
          placeholder="New room name (e.g. general)"
          value={newRoomName}
          onChange={(e) => setNewRoomName(e.target.value)}
        />
        <button type="submit">+ Create Room</button>
      </form>

      {loading ? (
        <p>Loading rooms...</p>
      ) : rooms.length === 0 ? (
        <p className="empty-state">No rooms yet. Create the first one!</p>
      ) : (
        <div className="room-grid">
          {rooms.map((room) => (
            <div key={room.id} className="room-card" onClick={() => handleJoinAndEnter(room)}>
              <h3>#{room.name}</h3>
              <p>{room.member_count} member{room.member_count !== 1 ? 's' : ''}</p>
              <span className="created-by">by {room.created_by}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
