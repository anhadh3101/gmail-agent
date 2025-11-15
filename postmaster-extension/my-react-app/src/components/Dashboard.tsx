import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import type { UserCredential } from 'firebase/auth';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState<'needsLead' | 'noLead'>('needsLead');
  const emailsNeedingLead = [
    { id: '1', subject: 'Follow-up required', preview: 'Client asked for a call recap...' },
    { id: '2', subject: 'New inbound from ACME', preview: 'Need to qualify the lead before...' },
  ];
  const emailsWithoutLead = [
    { id: '3', subject: 'Monthly newsletter', preview: 'Classified as info only...' },
    { id: '4', subject: 'Internal update', preview: 'No lead action needed...' },
  ];
  
  // Get userCredential from navigation state
  const userCredential = (location.state as { userCredential?: UserCredential })?.userCredential;
  console.log(userCredential);
  // Example: Log userCredential when available (you can replace this with your logic)
  useEffect(() => {
    if (userCredential) {
      console.log('User credentials received:', userCredential);
    }
  }, [userCredential]);

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
          <h2>Inbox Overview</h2>
          <div className="tab-header">
            <button
              className={`tab-button ${activeTab === 'needsLead' ? 'active' : ''}`}
              onClick={() => setActiveTab('needsLead')}
            >
              Needs Lead ({emailsNeedingLead.length})
            </button>
            <button
              className={`tab-button ${activeTab === 'noLead' ? 'active' : ''}`}
              onClick={() => setActiveTab('noLead')}
            >
              Classified w/out Lead ({emailsWithoutLead.length})
            </button>
          </div>
          <div className="tab-panel">
            {(activeTab === 'needsLead' ? emailsNeedingLead : emailsWithoutLead).map((email) => (
              <div key={email.id} className="email-row">
                <h3>{email.subject}</h3>
                <p>{email.preview}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
