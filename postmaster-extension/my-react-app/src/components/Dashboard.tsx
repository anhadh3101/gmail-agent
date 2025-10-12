import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Failed to log out:', error);
    }
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Welcome to Your Dashboard</h1>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </div>
      <div className="dashboard-content">
        <div className="user-info">
          <h2>User Information</h2>
          <p><strong>Email:</strong> {currentUser?.email}</p>
          <p><strong>User ID:</strong> {currentUser?.uid}</p>
          <p><strong>Email Verified:</strong> {currentUser?.emailVerified ? 'Yes' : 'No'}</p>
        </div>
        <div className="dashboard-section">
          <h2>Quick Actions</h2>
          <div className="action-cards">
            <div className="action-card">
              <h3>Gmail Integration</h3>
              <p>Connect your Gmail account to get started</p>
              <button className="action-button">Connect Gmail</button>
            </div>
            <div className="action-card">
              <h3>Settings</h3>
              <p>Manage your account settings</p>
              <button className="action-button">Go to Settings</button>
            </div>
            <div className="action-card">
              <h3>Analytics</h3>
              <p>View your email analytics</p>
              <button className="action-button">View Analytics</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
