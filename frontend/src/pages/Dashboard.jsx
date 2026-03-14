import React, { useEffect, useState } from 'react';
import { dashboardAPI } from '../services/api';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const mockChartData = [
  { name: 'Jan', income: 4200, expenses: 2800 },
  { name: 'Feb', income: 3800, expenses: 3100 },
  { name: 'Mar', income: 5200, expenses: 2400 },
  { name: 'Apr', income: 4700, expenses: 3600 },
  { name: 'May', income: 6100, expenses: 2900 },
  { name: 'Jun', income: 5400, expenses: 3200 },
  { name: 'Jul', income: 7200, expenses: 4100 },
];

const txnTypeIcon = (type) => {
  const map = { DEPOSIT: 'deposit', WITHDRAWAL: 'withdrawal', TRANSFER: 'transfer', PAYMENT: 'payment' };
  return map[type] || 'transfer';
};

const txnIcon = (type) => {
  const map = { DEPOSIT: 'bi-arrow-down-circle-fill', WITHDRAWAL: 'bi-arrow-up-circle-fill', TRANSFER: 'bi-arrow-left-right', PAYMENT: 'bi-receipt' };
  return map[type] || 'bi-arrow-left-right';
};

const formatDate = (iso) => new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });

const Dashboard = ({ onNavigate }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardAPI.get()
      .then(r => setData(r.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="loading-screen">
      <div className="spinner dark"></div>
      <span>Loading dashboard…</span>
    </div>
  );

  const primaryAccount = data?.accounts?.[0];

  return (
    <div>
      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon blue"><i className="bi bi-wallet2"></i></div>
          <div className="stat-info">
            <div className="stat-label">Total Balance</div>
            <div className="stat-value">${parseFloat(data?.total_balance || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
            <div className="stat-change up"><i className="bi bi-arrow-up-short"></i>3.2% this month</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon green"><i className="bi bi-credit-card-2-front"></i></div>
          <div className="stat-info">
            <div className="stat-label">Active Cards</div>
            <div className="stat-value">{data?.active_cards ?? 0}</div>
            <div className="stat-change" style={{ color: 'var(--gray-500)' }}>Debit & Credit</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon orange"><i className="bi bi-bank2"></i></div>
          <div className="stat-info">
            <div className="stat-label">Active Loans</div>
            <div className="stat-value">{data?.active_loans ?? 0}</div>
            <div className="stat-change" style={{ color: 'var(--gray-500)' }}>Outstanding</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon red"><i className="bi bi-bell"></i></div>
          <div className="stat-info">
            <div className="stat-label">Notifications</div>
            <div className="stat-value">{data?.unread_notifications ?? 0}</div>
            <div className="stat-change" style={{ color: 'var(--gray-500)' }}>Unread</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        {[
          { label: 'Deposit', icon: 'bi-arrow-down-circle', page: 'accounts' },
          { label: 'Withdraw', icon: 'bi-arrow-up-circle', page: 'accounts' },
          { label: 'Transfer', icon: 'bi-send', page: 'transfer' },
          { label: 'Pay Bill', icon: 'bi-receipt', page: 'transactions' },
        ].map(action => (
          <button key={action.label} className="quick-action-btn" onClick={() => onNavigate(action.page)}>
            <div className="quick-action-icon"><i className={`bi ${action.icon}`}></i></div>
            <span className="quick-action-label">{action.label}</span>
          </button>
        ))}
      </div>

      <div className="grid-2">
        {/* Primary Bank Card */}
        <div>
          <div className="d-flex justify-between align-center mb-3">
            <h3 className="card-title">My Primary Account</h3>
            <button className="btn btn-ghost btn-sm" onClick={() => onNavigate('accounts')}>
              View All <i className="bi bi-arrow-right"></i>
            </button>
          </div>
          {primaryAccount ? (
            <div className="bank-card blue">
              <div className="bank-card-top">
                <div className="bank-card-chip"><i className="bi bi-sim-fill"></i></div>
                <div className="bank-card-network">NOVAPAY</div>
              </div>
              <div className="bank-card-number">
                {primaryAccount.account_number.replace(/(.{4})/g, '$1  ').trim()}
              </div>
              <div className="bank-card-bottom">
                <div>
                  <div className="bank-card-label">Account Holder</div>
                  <div className="bank-card-value">{primaryAccount.user_name}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div className="bank-card-label">Balance</div>
                  <div className="bank-card-value">${parseFloat(primaryAccount.balance).toLocaleString()}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div className="bank-card-label">Type</div>
                  <div className="bank-card-value">{primaryAccount.account_type}</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="card">
              <div className="empty-state">
                <i className="bi bi-wallet2"></i>
                <h3>No accounts yet</h3>
                <p>Create your first account to get started</p>
              </div>
            </div>
          )}

          {/* Accounts list */}
          {data?.accounts?.length > 1 && (
            <div className="card mt-3">
              {data.accounts.slice(1).map(acc => (
                <div key={acc.id} className="d-flex align-center justify-between" style={{ padding: '0.75rem 0', borderBottom: '1px solid var(--gray-50)' }}>
                  <div className="d-flex align-center gap-3">
                    <div className="stat-icon blue" style={{ width: 36, height: 36, fontSize: '1rem' }}>
                      <i className="bi bi-wallet2"></i>
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{acc.account_type}</div>
                      <div className="text-muted">{acc.account_number}</div>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 700, fontFamily: 'var(--font-display)' }}>${parseFloat(acc.balance).toLocaleString()}</div>
                    <span className={`pill ${acc.status === 'ACTIVE' ? 'success' : 'neutral'}`}>{acc.status}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Chart */}
        <div>
          <div className="d-flex justify-between align-center mb-3">
            <h3 className="card-title">Income vs Expenses</h3>
            <span className="text-muted text-sm">Last 7 months</span>
          </div>
          <div className="card" style={{ padding: '1.25rem 1rem' }}>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={mockChartData}>
                <defs>
                  <linearGradient id="colorIncome" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0057FF" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#0057FF" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorExpenses" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00C896" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#00C896" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#6B7280' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#6B7280' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ borderRadius: 10, border: '1px solid #E5E7EB', boxShadow: '0 4px 16px rgba(0,0,0,0.08)', fontSize: 13 }}
                  formatter={(v) => [`$${v.toLocaleString()}`, '']}
                />
                <Area type="monotone" dataKey="income" stroke="#0057FF" strokeWidth={2} fill="url(#colorIncome)" name="Income" />
                <Area type="monotone" dataKey="expenses" stroke="#00C896" strokeWidth={2} fill="url(#colorExpenses)" name="Expenses" />
              </AreaChart>
            </ResponsiveContainer>
            <div className="d-flex gap-3 justify-between" style={{ marginTop: '0.75rem', paddingLeft: '0.5rem' }}>
              <div className="d-flex align-center gap-2"><span style={{ width: 10, height: 10, borderRadius: 2, background: '#0057FF', display: 'inline-block' }}></span><span className="text-sm text-muted">Income</span></div>
              <div className="d-flex align-center gap-2"><span style={{ width: 10, height: 10, borderRadius: 2, background: '#00C896', display: 'inline-block' }}></span><span className="text-sm text-muted">Expenses</span></div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="card mt-4">
        <div className="card-header">
          <div>
            <div className="card-title">Recent Transactions</div>
            <div className="card-subtitle">Your latest activity</div>
          </div>
          <button className="btn btn-outline btn-sm" onClick={() => onNavigate('transactions')}>
            View All <i className="bi bi-arrow-right"></i>
          </button>
        </div>
        {data?.recent_transactions?.length === 0 ? (
          <div className="empty-state">
            <i className="bi bi-arrow-left-right"></i>
            <h3>No transactions yet</h3>
            <p>Your recent transactions will appear here</p>
          </div>
        ) : (
          (data?.recent_transactions || []).map((txn) => (
            <div key={txn.id} className="txn-item">
              <div className={`txn-icon ${txnTypeIcon(txn.transaction_type)}`}>
                <i className={`bi ${txnIcon(txn.transaction_type)}`}></i>
              </div>
              <div className="txn-info">
                <div className="txn-name">{txn.description || txn.transaction_type}</div>
                <div className="txn-date">{formatDate(txn.created_at)} · Ref: {txn.reference}</div>
              </div>
              <div>
                <div className={`txn-amount ${txn.transaction_type === 'DEPOSIT' ? 'credit' : 'debit'}`}>
                  {txn.transaction_type === 'DEPOSIT' ? '+' : '-'}${parseFloat(txn.amount).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </div>
                <span className={`pill ${txn.status === 'COMPLETED' ? 'success' : txn.status === 'PENDING' ? 'warning' : 'danger'}`} style={{ float: 'right', marginTop: 4 }}>
                  {txn.status}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Dashboard;