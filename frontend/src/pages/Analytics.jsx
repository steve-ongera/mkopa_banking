import React, { useEffect, useState } from 'react';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { analyticsAPI, accountsAPI } from '../services/api.js';

const COLORS = ['#0057FF', '#00C896', '#FFB300', '#FF4757', '#9B59B6', '#1ABC9C'];

const TYPE_LABELS = {
  DEPOSIT: 'Deposits', WITHDRAWAL: 'Withdrawals', TRANSFER: 'Transfers',
  PAYMENT: 'Payments', FEE: 'Fees', INTEREST: 'Interest', REFUND: 'Refunds',
};

const fmt = (v) => `$${Number(v).toLocaleString('en-US', { minimumFractionDigits: 0 })}`;

const Analytics = () => {
  const [data, setData] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [selectedAcc, setSelectedAcc] = useState(null);
  const [statement, setStatement] = useState(null);
  const [stmtDates, setStmtDates] = useState({ start: '', end: '' });
  const [loading, setLoading] = useState(true);
  const [stmtLoading, setStmtLoading] = useState(false);

  useEffect(() => {
    Promise.all([analyticsAPI.spending(), accountsAPI.list()])
      .then(([sp, ac]) => {
        setData(sp.data);
        setAccounts(ac.data);
        if (ac.data.length > 0) setSelectedAcc(ac.data[0]);
      })
      .finally(() => setLoading(false));
  }, []);

  const loadStatement = () => {
    if (!selectedAcc) return;
    setStmtLoading(true);
    const params = {};
    if (stmtDates.start) params.start_date = stmtDates.start;
    if (stmtDates.end) params.end_date = stmtDates.end;
    analyticsAPI.statement(selectedAcc.id, params)
      .then(r => setStatement(r.data))
      .finally(() => setStmtLoading(false));
  };

  if (loading) return (
    <div className="loading-screen"><div className="spinner dark"></div><span>Loading analytics…</span></div>
  );

  const monthly = data?.monthly || [];
  const breakdown = data?.current_month_breakdown || [];

  const pieData = breakdown.map((b, i) => ({
    name: TYPE_LABELS[b.transaction_type] || b.transaction_type,
    value: parseFloat(b.total),
    count: b.count,
    color: COLORS[i % COLORS.length],
  }));

  const currentMonth = monthly[monthly.length - 1] || {};
  const prevMonth = monthly[monthly.length - 2] || {};
  const incomeChange = prevMonth.income ? ((currentMonth.income - prevMonth.income) / prevMonth.income * 100).toFixed(1) : 0;
  const expensesChange = prevMonth.expenses ? ((currentMonth.expenses - prevMonth.expenses) / prevMonth.expenses * 100).toFixed(1) : 0;

  return (
    <div>
      {/* Summary Stats */}
      <div className="stats-grid mb-4">
        {[
          { label: 'This Month Income', value: fmt(currentMonth.income || 0), icon: 'bi-arrow-down-circle', color: 'green', change: `${incomeChange >= 0 ? '+' : ''}${incomeChange}% vs last month`, up: incomeChange >= 0 },
          { label: 'This Month Expenses', value: fmt(currentMonth.expenses || 0), icon: 'bi-arrow-up-circle', color: 'red', change: `${expensesChange >= 0 ? '+' : ''}${expensesChange}% vs last month`, up: expensesChange < 0 },
          { label: 'Net Cash Flow', value: fmt(currentMonth.net || 0), icon: 'bi-graph-up-arrow', color: (currentMonth.net || 0) >= 0 ? 'green' : 'red', change: (currentMonth.net || 0) >= 0 ? 'Positive flow' : 'Negative flow', up: (currentMonth.net || 0) >= 0 },
          { label: 'Transactions', value: breakdown.reduce((s, b) => s + b.count, 0), icon: 'bi-arrow-left-right', color: 'blue', change: 'This month', up: true },
        ].map(({ label, value, icon, color, change, up }) => (
          <div key={label} className="stat-card">
            <div className={`stat-icon ${color}`}><i className={`bi ${icon}`}></i></div>
            <div className="stat-info">
              <div className="stat-label">{label}</div>
              <div className="stat-value">{value}</div>
              <div className={`stat-change ${up ? 'up' : 'down'}`}>
                <i className={`bi bi-arrow-${up ? 'up' : 'down'}-short`}></i>{change}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid-2 mb-4">
        {/* Income vs Expenses Area Chart */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Income vs Expenses</div>
              <div className="card-subtitle">6-month trend</div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={monthly}>
              <defs>
                <linearGradient id="gIncome" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0057FF" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#0057FF" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gExpenses" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#FF4757" stopOpacity={0.12} />
                  <stop offset="95%" stopColor="#FF4757" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#6B7280' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#6B7280' }} axisLine={false} tickLine={false} tickFormatter={v => `$${(v/1000).toFixed(0)}k`} />
              <Tooltip formatter={(v) => [fmt(v), '']} contentStyle={{ borderRadius: 10, border: '1px solid #E5E7EB', fontSize: 12 }} />
              <Legend />
              <Area type="monotone" dataKey="income" name="Income" stroke="#0057FF" strokeWidth={2} fill="url(#gIncome)" dot={{ r: 3, fill: '#0057FF' }} />
              <Area type="monotone" dataKey="expenses" name="Expenses" stroke="#FF4757" strokeWidth={2} fill="url(#gExpenses)" dot={{ r: 3, fill: '#FF4757' }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Net Cash Flow Bar */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Net Cash Flow</div>
              <div className="card-subtitle">Monthly surplus / deficit</div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={monthly}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#6B7280' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#6B7280' }} axisLine={false} tickLine={false} tickFormatter={v => `$${(v/1000).toFixed(0)}k`} />
              <Tooltip formatter={(v) => [fmt(v), 'Net']} contentStyle={{ borderRadius: 10, border: '1px solid #E5E7EB', fontSize: 12 }} />
              <Bar dataKey="net" name="Net" radius={[4, 4, 0, 0]}>
                {monthly.map((entry, i) => (
                  <Cell key={i} fill={entry.net >= 0 ? '#00C896' : '#FF4757'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Breakdown + Pie */}
      <div className="grid-2 mb-4">
        {/* Pie Chart */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Transaction Breakdown</div>
            <div className="card-subtitle">Current month by type</div>
          </div>
          {pieData.length === 0 ? (
            <div className="empty-state" style={{ padding: '2rem' }}>
              <i className="bi bi-pie-chart"></i>
              <h3>No data yet</h3>
              <p>Make some transactions this month</p>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
              <ResponsiveContainer width={160} height={160}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={3} dataKey="value">
                    {pieData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v) => [fmt(v), '']} />
                </PieChart>
              </ResponsiveContainer>
              <div style={{ flex: 1 }}>
                {pieData.map((entry, i) => (
                  <div key={i} className="d-flex justify-between align-center" style={{ padding: '4px 0', borderBottom: '1px solid var(--gray-50)' }}>
                    <div className="d-flex align-center gap-2">
                      <div style={{ width: 8, height: 8, borderRadius: 2, background: entry.color, flexShrink: 0 }}></div>
                      <span className="text-sm">{entry.name}</span>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div className="text-sm fw-600">{fmt(entry.value)}</div>
                      <div className="text-xs text-muted">{entry.count} txns</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Monthly Table */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Monthly Summary</div>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Income</th>
                  <th>Expenses</th>
                  <th>Net</th>
                </tr>
              </thead>
              <tbody>
                {[...monthly].reverse().map((m, i) => (
                  <tr key={i}>
                    <td className="fw-600">{m.month} {m.year}</td>
                    <td style={{ color: 'var(--success)' }}>{fmt(m.income)}</td>
                    <td style={{ color: 'var(--danger)' }}>{fmt(m.expenses)}</td>
                    <td>
                      <span className={`txn-amount ${m.net >= 0 ? 'credit' : 'debit'}`}>
                        {m.net >= 0 ? '+' : ''}{fmt(m.net)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Account Statement */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Account Statement</div>
            <div className="card-subtitle">Full transaction ledger with running balance</div>
          </div>
        </div>
        <div className="d-flex gap-3 align-center mb-4" style={{ flexWrap: 'wrap' }}>
          <div style={{ flex: '1 1 200px' }}>
            <label className="form-label">Account</label>
            <select className="form-control" value={selectedAcc?.id || ''} onChange={e => setSelectedAcc(accounts.find(a => a.id === e.target.value))}>
              {accounts.map(a => <option key={a.id} value={a.id}>{a.account_type} — {a.account_number}</option>)}
            </select>
          </div>
          <div style={{ flex: '1 1 150px' }}>
            <label className="form-label">From</label>
            <input className="form-control" type="date" value={stmtDates.start} onChange={e => setStmtDates(d => ({ ...d, start: e.target.value }))} />
          </div>
          <div style={{ flex: '1 1 150px' }}>
            <label className="form-label">To</label>
            <input className="form-control" type="date" value={stmtDates.end} onChange={e => setStmtDates(d => ({ ...d, end: e.target.value }))} />
          </div>
          <div style={{ paddingTop: '1.5rem' }}>
            <button className="btn btn-primary" onClick={loadStatement} disabled={stmtLoading}>
              {stmtLoading ? <><span className="spinner"></span> Loading…</> : <><i className="bi bi-file-earmark-text"></i> Generate</>}
            </button>
          </div>
        </div>

        {statement && (
          <>
            {/* Summary row */}
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
              {[
                { label: 'Total Credits', value: fmt(statement.summary.total_credits), color: 'var(--success)' },
                { label: 'Total Debits', value: fmt(statement.summary.total_debits), color: 'var(--danger)' },
                { label: 'Net', value: fmt(statement.summary.net), color: statement.summary.net >= 0 ? 'var(--success)' : 'var(--danger)' },
                { label: 'Transactions', value: statement.summary.transaction_count, color: 'var(--primary)' },
                { label: 'Current Balance', value: fmt(statement.current_balance), color: 'var(--dark)' },
              ].map(({ label, value, color }) => (
                <div key={label} style={{ background: 'var(--gray-50)', borderRadius: 'var(--radius-sm)', padding: '0.75rem 1rem', flex: '1 1 140px' }}>
                  <div className="text-xs text-muted fw-600" style={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</div>
                  <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.1rem', color, marginTop: 4 }}>{value}</div>
                </div>
              ))}
            </div>

            {statement.statement.length === 0 ? (
              <div className="empty-state"><i className="bi bi-file-earmark-text"></i><h3>No transactions in this period</h3></div>
            ) : (
              <div className="table-container" style={{ maxHeight: 400, overflowY: 'auto' }}>
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Description</th>
                      <th>Reference</th>
                      <th>Credit</th>
                      <th>Debit</th>
                      <th>Balance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {statement.statement.map((row, i) => (
                      <tr key={i}>
                        <td className="text-xs text-muted">{row.date}</td>
                        <td>
                          <div className="fw-600 text-sm">{row.description}</div>
                          <div className="text-xs text-muted">{row.type}</div>
                        </td>
                        <td><span className="font-mono text-xs">{row.reference?.slice(0, 14)}</span></td>
                        <td style={{ color: 'var(--success)', fontWeight: 600 }}>{row.credit ? fmt(row.credit) : '—'}</td>
                        <td style={{ color: 'var(--danger)', fontWeight: 600 }}>{row.debit ? fmt(row.debit) : '—'}</td>
                        <td style={{ fontFamily: 'var(--font-display)', fontWeight: 700 }}>{fmt(row.balance)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}

        {!statement && !stmtLoading && (
          <div className="empty-state" style={{ padding: '2rem' }}>
            <i className="bi bi-file-earmark-bar-graph"></i>
            <h3>Select an account and generate a statement</h3>
            <p>Filter by date range or leave blank to see all transactions</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Analytics;