import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { api } from './api/client';
import Login from './components/Login';
import Register from './components/Register';
import RoomList from './components/RoomList';
import ChatRoom from './components/ChatRoom';

function ProtectedRoute({ children }) {
  return api.isLoggedIn() ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<ProtectedRoute><RoomList /></ProtectedRoute>} />
        <Route path="/room/:id/:slug" element={<ProtectedRoute><ChatRoom /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  );
}
