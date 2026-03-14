import React, { useEffect, useState } from 'react';
import { loansAPI, accountsAPI } from '../services/api';

const Loans = () => {
  const [loans, setLoans] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showApply, setShowApply] = useState(false);
  const [form, setForm] = useState({ account_id: '', loan_type: 'PERSONAL', amount: '', tenure_months: 12, purpose: '' });
  const [applying, setApplying] = useState(false);
  const [alert, setAlert] = useState(null);
  const [calc, setCalc] = useState(null);

  useEffect(() => {
    Promise.all([loansAPI.list(), accountsAPI.list()])
      .then(([l, a]) => { setLoans(l.data); setAccounts(a.data); if (a.data.length) setForm(f => ({ ...f, account_id: a.data[0].id })); })
      .finally(() => setLoading(false));
  }, []);

  const set = (key) => (e) => {
    setForm(f => ({ ...f, [key]: e.target.value }));
  };

  const computeCalc = () => {
    if (!form.amount || !form.tenure_months) { setCalc(null); return; }
    const r = 12 / 12 / 100;
    const p = parseFloat(form.amount);
    const n = parseInt(form.tenure_months);
    const monthly = r > 0 ? p * r * Math.pow(1 + r, n) / (Math.pow(1 + r, n) - 1) : p / n;
    setCalc({ monthly: monthly.toFixed(2), total: (monthly * n).toFixed(2), interest: (monthly * n - p).toFixed(2) });
  };

  const handleApply = async () => {
    setApplying(true);
    try {
      const { data } = await loansAPI.apply({ ...form, amount: parseFloat(form.amount), tenure_months: parseInt(form.tenure_months) });
      setLoans(ls => [data, ...ls]);
      setAlert({ type: 'success', msg: 'Loan application submitted successfully! Awaiting approval.' });
      setShowApply(false);
      setCalc(null);
    } catch (e) {
      setAlert({ type: 'error', msg: e.response?.data?.error || 'Application failed' });
    } finally { setApplying(false); }
  };

  const STATUS_COLOR = { PENDING: 'warning', APPROVED: 'info', ACTIVE: 'success', PAID: 'neutral', DEFAULTED: 'danger', REJECTED: 'danger' };

  if (loading) return <div className="loading-screen"><div className="spinner dark"></div></div>;

  return (
    <div>
      {alert && (
        <div className={`alert ${alert.type}`}>
          <i className={`bi ${alert.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill'}`}></i>
          <span>{alert.msg}</span>
        </div>
      )}

      <div className="d-flex justify-between align-center mb-4">
        <div></div>
        <button className="btn btn-primary" onClick={() => setShowApply(true)}>
          <i className="bi bi-plus-lg"></i> Apply for Loan
        </button>
      </div>

      {/* Loan Stats */}
      <div className="stats-grid mb-4">
        {[
          { label: 'Total Applications', value: loans.length, icon: 'bi-file-earmark-text', color: 'blue' },
          { label: 'Active Loans', value: loans.filter(l => l.status === 'ACTIVE').length, icon: 'bi-bank2', color: 'green' },
          { label: 'Pending', value: loans.filter(l => l.status === 'PENDING').length, icon: 'bi-clock', color: 'orange' },
          { label: 'Total Outstanding', value: `$${loans.filter(l => l.status === 'ACTIVE').reduce((s, l) => s + parseFloat(l.outstanding_balance), 0).toLocaleString()}`, icon: 'bi-cash-stack', color: 'red' },
        ].map(({ label, value, icon, color }) => (
          <div key={label} className="stat-card">
            <div className={`stat-icon ${color}`}><i className={`bi ${icon}`}></i></div>
            <div className="stat-info"><div className="stat-label">{label}</div><div className="stat-value">{value}</div></div>
          </div>
        ))}
      </div>

      {loans.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <i className="bi bi-bank2"></i>
            <h3>No loan applications yet</h3>
            <p>Apply for a personal, mortgage, or business loan</p>
            <button className="btn btn-primary mt-3" onClick={() => setShowApply(true)}>Apply Now</button>
          </div>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
          {loans.map(loan => (
            <div key={loan.id} className="card">
              <div className="d-flex justify-between align-center mb-3">
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{loan.loan_type} Loan</div>
                  <div className="text-muted text-sm">{loan.tenure_months} months · {loan.interest_rate}% p.a.</div>
                </div>
                <span className={`pill ${STATUS_COLOR[loan.status]}`}>{loan.status}</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
                {[
                  { label: 'Principal', value: `$${parseFloat(loan.principal_amount).toLocaleString()}` },
                  { label: 'Outstanding', value: `$${parseFloat(loan.outstanding_balance).toLocaleString()}` },
                  { label: 'Monthly EMI', value: `$${parseFloat(loan.monthly_installment).toLocaleString()}` },
                  { label: 'Next Payment', value: loan.next_payment_date || '—' },
                ].map(({ label, value }) => (
                  <div key={label} style={{ background: 'var(--gray-50)', borderRadius: 'var(--radius-sm)', padding: '0.65rem 0.75rem' }}>
                    <div className="text-xs text-muted" style={{ textTransform: 'uppercase', letterSpacing: '0.04em', fontWeight: 600 }}>{label}</div>
                    <div style={{ fontWeight: 700, fontSize: '0.9rem', marginTop: 3 }}>{value}</div>
                  </div>
                ))}
              </div>
              {loan.purpose && <div className="text-sm text-muted" style={{ borderTop: '1px solid var(--gray-50)', paddingTop: '0.75rem' }}>Purpose: {loan.purpose}</div>}
              {/* Progress bar for active loans */}
              {loan.status === 'ACTIVE' && (
                <div style={{ marginTop: '0.75rem' }}>
                  <div className="d-flex justify-between text-xs text-muted mb-1">
                    <span>Repaid</span>
                    <span>{Math.round((1 - parseFloat(loan.outstanding_balance) / parseFloat(loan.principal_amount)) * 100)}%</span>
                  </div>
                  <div style={{ height: 6, background: 'var(--gray-100)', borderRadius: 3, overflow: 'hidden' }}>
                    <div style={{ height: '100%', background: 'var(--primary)', borderRadius: 3, width: `${Math.round((1 - parseFloat(loan.outstanding_balance) / parseFloat(loan.principal_amount)) * 100)}%` }}></div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Apply Modal */}
      {showApply && (
        <div className="modal-overlay" onClick={() => setShowApply(false)}>
          <div className="modal" style={{ maxWidth: 520 }} onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title"><i className="bi bi-bank2" style={{ color: 'var(--primary)', marginRight: 8 }}></i>Loan Application</div>
              <button className="modal-close" onClick={() => setShowApply(false)}><i className="bi bi-x"></i></button>
            </div>
            <div className="form-group">
              <label className="form-label">Account</label>
              <select className="form-control" value={form.account_id} onChange={set('account_id')}>
                {accounts.map(a => <option key={a.id} value={a.id}>{a.account_type} — {a.account_number}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Loan Type</label>
              <select className="form-control" value={form.loan_type} onChange={set('loan_type')}>
                {['PERSONAL', 'MORTGAGE', 'AUTO', 'BUSINESS', 'STUDENT'].map(t => <option key={t}>{t}</option>)}
              </select>
            </div>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Loan Amount</label>
                <div className="input-group">
                  <span className="input-prefix">$</span>
                  <input className="form-control" type="number" placeholder="0.00" value={form.amount} onChange={set('amount')} min="100" onBlur={computeCalc} />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Tenure (months)</label>
                <input className="form-control" type="number" value={form.tenure_months} onChange={set('tenure_months')} min="1" max="360" onBlur={computeCalc} />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Purpose</label>
              <input className="form-control" type="text" placeholder="Brief loan purpose" value={form.purpose} onChange={set('purpose')} />
            </div>
            {calc && (
              <div className="alert info" style={{ marginBottom: '1rem' }}>
                <i className="bi bi-calculator"></i>
                <div>
                  <div style={{ fontWeight: 700, marginBottom: 4 }}>EMI Estimate (12% p.a.)</div>
                  Monthly: <strong>${calc.monthly}</strong> · Total: <strong>${calc.total}</strong> · Interest: <strong>${calc.interest}</strong>
                </div>
              </div>
            )}
            <div className="d-flex gap-2">
              <button className="btn btn-ghost" style={{ flex: 1 }} onClick={() => setShowApply(false)}>Cancel</button>
              <button className="btn btn-primary" style={{ flex: 1 }} onClick={handleApply} disabled={applying || !form.amount || !form.account_id}>
                {applying ? <><span className="spinner"></span> Submitting…</> : <><i className="bi bi-check-lg"></i> Submit Application</>}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Loans;