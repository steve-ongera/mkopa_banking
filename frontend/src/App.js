import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './components/AuthContext';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Accounts from './pages/Accounts';
import Transactions from './pages/Transactions';
import Transfer from './pages/Transfer';
import Cards from './pages/Cards';
import Loans from './pages/Loans';
import Beneficiaries from './pages/Beneficiaries';
import Notifications from './pages/Notifications';
import Profile from './pages/Profile';
import Analytics from './pages/Analytics';
import { notificationsAPI } from './services/api';
import './styles/main.css';

const AppContent = () => {
  const { user, loading } = useAuth();
  const [page, setPage] = useState('dashboard');
  const [authPage, setAuthPage] = useState('login');
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (user) {
      notificationsAPI.list().then(r => {
        setUnreadCount(r.data.filter(n => !n.is_read).length);
      }).catch(() => {});
    }
  }, [user]);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', flexDirection: 'column', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: '1rem' }}>
          <div className="logo-icon"><i className="bi bi-shield-check"></i></div>
          <div className="logo-text">Nova<span>Pay</span></div>
        </div>
        <div className="spinner dark"></div>
        <span style={{ color: 'var(--gray-500)', fontSize: '0.875rem' }}>Loading your banking dashboard…</span>
      </div>
    );
  }

  if (!user) {
    return authPage === 'login'
      ? <Login onSwitchToRegister={() => setAuthPage('register')} />
      : <Register onSwitchToLogin={() => setAuthPage('login')} />;
  }

  const renderPage = () => {
    switch (page) {
      case 'dashboard':     return <Dashboard onNavigate={setPage} />;
      case 'accounts':      return <Accounts />;
      case 'transactions':  return <Transactions />;
      case 'transfer':      return <Transfer />;
      case 'cards':         return <Cards />;
      case 'loans':         return <Loans />;
      case 'beneficiaries': return <Beneficiaries />;
      case 'notifications': return <Notifications onRead={() => setUnreadCount(c => Math.max(0, c - 1))} />;
      case 'profile':       return <Profile />;
      case 'analytics':     return <Analytics />;
      default:              return <Dashboard onNavigate={setPage} />;
    }
  };

  return (
    <div className="app-layout">
      <Sidebar currentPage={page} onNavigate={setPage} unreadCount={unreadCount} />
      <div className="main-content">
        <Topbar currentPage={page} onNavigate={setPage} unreadCount={unreadCount} user={user} />
        <div className="page-content">
          {renderPage()}
        </div>
      </div>
    </div>
  );
};

const App = () => (
  <AuthProvider>
    <AppContent />
  </AuthProvider>
);

export default App;