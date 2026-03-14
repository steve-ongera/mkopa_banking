import React from 'react';
import { useAuth } from './AuthContext';

const NAV_ITEMS = [
  { label: 'Dashboard',     icon: 'bi-grid-1x2-fill',           page: 'dashboard',     section: 'main' },
  { label: 'Accounts',      icon: 'bi-wallet2',                  page: 'accounts',      section: 'main' },
  { label: 'Transactions',  icon: 'bi-arrow-left-right',         page: 'transactions',  section: 'main' },
  { label: 'Transfer',      icon: 'bi-send-fill',                page: 'transfer',      section: 'main' },
  { label: 'Analytics',     icon: 'bi-graph-up-arrow',           page: 'analytics',     section: 'main' },
  { label: 'Cards',         icon: 'bi-credit-card-2-front-fill', page: 'cards',         section: 'services' },
  { label: 'Loans',         icon: 'bi-bank2',                    page: 'loans',         section: 'services' },
  { label: 'Beneficiaries', icon: 'bi-people-fill',              page: 'beneficiaries', section: 'services' },
  { label: 'Profile',       icon: 'bi-person-fill',              page: 'profile',       section: 'account' },
  { label: 'Notifications', icon: 'bi-bell-fill',                page: 'notifications', section: 'account' },
];

const Sidebar = ({ currentPage, onNavigate, unreadCount }) => {
  const { user, logout } = useAuth();

  const sections = {
    main:     { label: 'Main Menu',         items: NAV_ITEMS.filter(i => i.section === 'main') },
    services: { label: 'Banking Services',  items: NAV_ITEMS.filter(i => i.section === 'services') },
    account:  { label: 'Account',           items: NAV_ITEMS.filter(i => i.section === 'account') },
  };

  const initials = user
    ? ((user.first_name?.[0] || '') + (user.last_name?.[0] || '')) || user.username?.[0]?.toUpperCase()
    : 'U';

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon"><i className="bi bi-shield-check"></i></div>
        <div className="logo-text">Nova<span>Pay</span></div>
      </div>

      <nav className="sidebar-nav">
        {Object.entries(sections).map(([key, { label, items }]) => (
          <div key={key}>
            <div className="nav-section-label">{label}</div>
            {items.map((item) => (
              <button
                key={item.page}
                className={`nav-item ${currentPage === item.page ? 'active' : ''}`}
                onClick={() => onNavigate(item.page)}
              >
                <i className={`bi ${item.icon}`}></i>
                <span>{item.label}</span>
                {item.page === 'notifications' && unreadCount > 0 && (
                  <span className="pill danger" style={{ marginLeft: 'auto', padding: '1px 7px', fontSize: '0.7rem' }}>
                    {unreadCount}
                  </span>
                )}
              </button>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="user-card" onClick={() => onNavigate('profile')}>
          <div className="user-avatar">{initials}</div>
          <div className="user-info">
            <div className="user-name">{user?.first_name || user?.username}</div>
            <div className="user-role">Personal Account</div>
          </div>
          <i className="bi bi-chevron-right" style={{ color: 'var(--gray-400)', fontSize: '0.75rem' }}></i>
        </div>
        <button className="nav-item" onClick={logout} style={{ color: 'var(--danger)' }}>
          <i className="bi bi-box-arrow-right"></i>
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;