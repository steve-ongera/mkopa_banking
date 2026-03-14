import React from 'react';

const PAGE_TITLES = {
  dashboard:     { title: 'Dashboard',       subtitle: 'Welcome back!' },
  accounts:      { title: 'My Accounts',     subtitle: 'Manage your bank accounts' },
  transactions:  { title: 'Transactions',    subtitle: 'Transaction history' },
  transfer:      { title: 'Transfer Money',  subtitle: 'Send funds securely' },
  analytics:     { title: 'Analytics',       subtitle: 'Spending insights & statements' },
  cards:         { title: 'Cards',           subtitle: 'Manage your debit & credit cards' },
  loans:         { title: 'Loans',           subtitle: 'Your loan portfolio' },
  beneficiaries: { title: 'Beneficiaries',   subtitle: 'Saved payees' },
  profile:       { title: 'Profile',         subtitle: 'Account settings' },
  notifications: { title: 'Notifications',   subtitle: 'Alerts and updates' },
};

const Topbar = ({ currentPage, onNavigate, unreadCount, user }) => {
  const { title, subtitle } = PAGE_TITLES[currentPage] || { title: currentPage, subtitle: '' };

  return (
    <header className="topbar">
      <div className="topbar-left">
        <div className="page-title">{title}</div>
        <div className="page-subtitle">{subtitle}</div>
      </div>
      <div className="topbar-right">
        <button className="topbar-btn" onClick={() => onNavigate('notifications')} title="Notifications">
          <i className="bi bi-bell"></i>
          {unreadCount > 0 && <span className="badge">{unreadCount > 9 ? '9+' : unreadCount}</span>}
        </button>
        <button className="topbar-btn" onClick={() => onNavigate('profile')} title="Profile">
          <i className="bi bi-person"></i>
        </button>
      </div>
    </header>
  );
};

export default Topbar;