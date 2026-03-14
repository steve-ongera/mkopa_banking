import React, { useEffect, useState } from 'react';
import { accountsAPI, transactionsAPI, beneficiariesAPI } from '../services/api';

const Transfer = () => {
  const [accounts, setAccounts] = useState([]);
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [form, setForm] = useState({ from_account_id: '', to_account_number: '', amount: '', description: '' });
  const [loading, setLoading] = useState(false);
  const [pageLoading, setPageLoading] = useState(true);
  const [alert, setAlert] = useState(null);
  const [preview, setPreview] = useState(null);

  useEffect(() => {
    Promise.all([accountsAPI.list(), beneficiariesAPI.list()])
      .then(([a, b]) => {
        setAccounts(a.data);
        setBeneficiaries(b.data);
        if (a.data.length > 0) setForm(f => ({ ...f, from_account_id: a.data[0].id }));
      })
      .finally(() => setPageLoading(false));
  }, []);

  const set = (key) => (e) => setForm(f => ({ ...f, [key]: e.target.value }));

  const selectedAccount = accounts.find(a => a.id === form.from_account_id);
  const fee = form.amount ? (parseFloat(form.amount) * 0.001).toFixed(2) : '0.00';
  const total = form.amount ? (parseFloat(form.amount) + parseFloat(fee)).toFixed(2) : '0.00';

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!preview) { setPreview(true); return; }
    setLoading(true);
    try {
      await transactionsAPI.transfer({
        from_account_id: form.from_account_id,
        to_account_number: form.to_account_number,
        amount: parseFloat(form.amount),
        description: form.description || 'Transfer',
      });
      setAlert({ type: 'success', msg: `Successfully transferred $${form.amount} to ${form.to_account_number}` });
      setForm(f => ({ ...f, to_account_number: '', amount: '', description: '' }));
      setPreview(false);
      const r = await accountsAPI.list();
      setAccounts(r.data);
    } catch (e) {
      setAlert({ type: 'error', msg: e.response?.data?.error || 'Transfer failed' });
      setPreview(false);
    } finally { setLoading(false); }
  };

  if (pageLoading) return <div className="loading-screen"><div className="spinner dark"></div></div>;

  return (
    <div style={{ maxWidth: 640, margin: '0 auto' }}>
      {alert && (
        <div className={`alert ${alert.type}`} style={{ marginBottom: '1.5rem' }}>
          <i className={`bi ${alert.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill'}`}></i>
          <span>{alert.msg}</span>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Send Money</div>
            <div className="card-subtitle">Transfer funds to any NovaPay account</div>
          </div>
          <div className="stat-icon blue"><i className="bi bi-send-fill"></i></div>
        </div>

        {!preview ? (
          <form onSubmit={handleSubmit}>
            {/* From Account */}
            <div className="form-group">
              <label className="form-label">From Account</label>
              <select className="form-control" value={form.from_account_id} onChange={set('from_account_id')} required>
                {accounts.map(acc => (
                  <option key={acc.id} value={acc.id}>
                    {acc.account_type} — {acc.account_number} (Balance: {acc.currency} {parseFloat(acc.balance).toLocaleString()})
                  </option>
                ))}
              </select>
              {selectedAccount && (
                <div className="form-hint">Available: {selectedAccount.currency} {parseFloat(selectedAccount.available_balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
              )}
            </div>

            {/* Beneficiaries Quick Select */}
            {beneficiaries.length > 0 && (
              <div className="form-group">
                <label className="form-label">Quick Select (Saved Beneficiaries)</label>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  {beneficiaries.slice(0, 6).map(b => (
                    <button
                      key={b.id} type="button"
                      className={`btn btn-sm ${form.to_account_number === b.account_number ? 'btn-primary' : 'btn-outline'}`}
                      onClick={() => setForm(f => ({ ...f, to_account_number: b.account_number }))}
                    >
                      <i className="bi bi-person-fill"></i> {b.nickname || b.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* To Account */}
            <div className="form-group">
              <label className="form-label">To Account Number</label>
              <div className="input-group">
                <i className="bi bi-hash input-icon"></i>
                <input
                  className="form-control font-mono"
                  type="text"
                  placeholder="Enter 12-digit account number"
                  value={form.to_account_number}
                  onChange={set('to_account_number')}
                  maxLength={12}
                  required
                />
              </div>
            </div>

            {/* Amount */}
            <div className="form-group">
              <label className="form-label">Amount</label>
              <div className="input-group">
                <span className="input-prefix">$</span>
                <input
                  className="form-control"
                  type="number"
                  placeholder="0.00"
                  value={form.amount}
                  onChange={set('amount')}
                  min="1" step="0.01"
                  required
                />
              </div>
            </div>

            {/* Description */}
            <div className="form-group">
              <label className="form-label">Narration (optional)</label>
              <input className="form-control" type="text" placeholder="e.g. Rent payment" value={form.description} onChange={set('description')} />
            </div>

            {/* Fee preview */}
            {form.amount && (
              <div style={{ background: 'var(--gray-50)', borderRadius: 'var(--radius-sm)', padding: '1rem', marginBottom: '1rem' }}>
                <div className="d-flex justify-between text-sm" style={{ marginBottom: 4 }}>
                  <span className="text-muted">Transfer Amount</span><span className="fw-600">${parseFloat(form.amount).toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
                </div>
                <div className="d-flex justify-between text-sm" style={{ marginBottom: 4 }}>
                  <span className="text-muted">Service Fee (0.1%)</span><span className="fw-600">${fee}</span>
                </div>
                <div className="divider" style={{ margin: '0.5rem 0' }}></div>
                <div className="d-flex justify-between" style={{ fontWeight: 700, fontFamily: 'var(--font-display)' }}>
                  <span>Total Deducted</span><span style={{ color: 'var(--primary)' }}>${total}</span>
                </div>
              </div>
            )}

            <button className="btn btn-primary btn-block btn-lg" type="submit">
              <i className="bi bi-arrow-right-circle"></i> Continue to Review
            </button>
          </form>
        ) : (
          /* Confirm Step */
          <div>
            <div className="alert info" style={{ marginBottom: '1.5rem' }}>
              <i className="bi bi-info-circle-fill"></i>
              <span>Please review the transfer details carefully before confirming.</span>
            </div>
            {[
              { label: 'From', value: `${selectedAccount?.account_type} — ${selectedAccount?.account_number}` },
              { label: 'To Account', value: form.to_account_number, mono: true },
              { label: 'Amount', value: `$${parseFloat(form.amount).toLocaleString('en-US', { minimumFractionDigits: 2 })}` },
              { label: 'Service Fee', value: `$${fee}` },
              { label: 'Total', value: `$${total}`, bold: true },
              { label: 'Description', value: form.description || '—' },
            ].map(({ label, value, mono, bold }) => (
              <div key={label} className="d-flex justify-between align-center" style={{ padding: '0.75rem 0', borderBottom: '1px solid var(--gray-50)' }}>
                <span className="text-muted text-sm">{label}</span>
                <span className={`${mono ? 'font-mono' : ''} ${bold ? 'fw-700' : 'fw-600'}`} style={bold ? { color: 'var(--primary)', fontSize: '1.05rem' } : {}}>
                  {value}
                </span>
              </div>
            ))}
            <div className="d-flex gap-2 mt-4">
              <button className="btn btn-ghost" style={{ flex: 1 }} onClick={() => setPreview(false)} disabled={loading}>
                <i className="bi bi-arrow-left"></i> Back
              </button>
              <button className="btn btn-primary" style={{ flex: 1 }} onClick={handleSubmit} disabled={loading}>
                {loading ? <><span className="spinner"></span> Processing…</> : <><i className="bi bi-check-circle-fill"></i> Confirm Transfer</>}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Transfer;