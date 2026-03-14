import React, { useEffect, useState } from 'react';
import { notificationsAPI } from '../services/api';

const TYPE_ICONS = { TRANSACTION: 'bi-arrow-left-right', SECURITY: 'bi-shield-exclamation', PROMO: 'bi-gift', SYSTEM: 'bi-info-circle' };
const TYPE_COLORS = { TRANSACTION: 'blue', SECURITY: 'red', PROMO: 'green', SYSTEM: 'orange' };

const Notifications = ({ onRead }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    notificationsAPI.list().then(r => setNotifications(r.data)).finally(() => setLoading(false));
  }, []);

  const markRead = async (n) => {
    if (n.is_read) return;
    await notificationsAPI.markRead(n.id);
    setNotifications(ns => ns.map(x => x.id === n.id ? { ...x, is_read: true } : x));
    onRead?.();
  };

  const markAll = async () => {
    await notificationsAPI.markAllRead();
    setNotifications(ns => ns.map(n => ({ ...n, is_read: true })));
    onRead?.();
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  if (loading) return <div className="loading-screen"><div className="spinner dark"></div></div>;

  return (
    <div>
      <div className="d-flex justify-between align-center mb-4">
        <span className="text-muted text-sm">{unreadCount} unread</span>
        {unreadCount > 0 && (
          <button className="btn btn-outline btn-sm" onClick={markAll}>
            <i className="bi bi-check2-all"></i> Mark All Read
          </button>
        )}
      </div>

      <div className="card" style={{ padding: 0 }}>
        {notifications.length === 0 ? (
          <div className="empty-state" style={{ padding: '3rem' }}>
            <i className="bi bi-bell-slash"></i><h3>No notifications</h3><p>You're all caught up!</p>
          </div>
        ) : (
          notifications.map((n, idx) => (
            <div
              key={n.id}
              onClick={() => markRead(n)}
              style={{
                display: 'flex', alignItems: 'flex-start', gap: '1rem',
                padding: '1rem 1.25rem',
                borderBottom: idx < notifications.length - 1 ? '1px solid var(--gray-50)' : 'none',
                cursor: n.is_read ? 'default' : 'pointer',
                background: n.is_read ? 'transparent' : 'rgba(0,87,255,0.02)',
                transition: 'background 0.15s',
              }}
            >
              <div className={`stat-icon ${TYPE_COLORS[n.notification_type] || 'blue'}`} style={{ width: 40, height: 40, fontSize: '1rem', flexShrink: 0 }}>
                <i className={`bi ${TYPE_ICONS[n.notification_type] || 'bi-bell'}`}></i>
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: n.is_read ? 500 : 700, fontSize: '0.9rem', marginBottom: 2 }}>{n.title}</div>
                <div className="text-muted text-sm" style={{ lineHeight: 1.5 }}>{n.message}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--gray-400)', marginTop: 4 }}>
                  {new Date(n.created_at).toLocaleString()}
                </div>
              </div>
              {!n.is_read && (
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--primary)', flexShrink: 0, marginTop: 6 }}></div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Notifications;