import React, { useEffect, useState } from 'react';
import { accountsAPI, transactionsAPI } from '../services/api';

const ACCOUNT_COLORS = ['blue', 'dark', 'green'];

const Accounts = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [txns, setTxns] = useState([]);
  const [txnLoading, setTxnLoading] = useState(false);
  const [showDeposit, setShowDeposit] = useState(false);
  const [showWithdraw, setShowWithdraw] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [alert, setAlert] = useState(null);
  const [newAccType, setNewAccType] = useState('SAVINGS');
  const [newAccCurrency, setNewAccCurrency] = useState('USD');

  useEffect(() => {
    accountsAPI.list().then(r => {
      setAccounts(r.data);
      if (r.data.length > 0) selectAccount(r.data[0].id, r.data);
    }).finally(() => setLoading(false));
  }, []);

  const selectAccount = (id, accs = accounts) => {
    const acc = accs.find(a => a.id === id);
    setSelected(acc);
    setTxnLoading(true);
    transactionsAPI.list({ account_id: id }).then(r => setTxns(r.data)).finally(() => setTxnLoading(false));
  };

  const showAlert = (type, msg) => {
    setAlert({ type, msg });
    setTimeout(() => setAlert(null), 4000);
  };

  const handleDeposit = async () => {
    if (!amount || isNaN(amount) || +amount <= 0) return;
    setActionLoading(true);
    try {
      await transactionsAPI.deposit({ account_id: selected.id, amount: parseFloat(amount), description });
      showAlert('success', `$${amount} deposited successfully!`);
      const r = await accountsAPI.list();
      setAccounts(r.data);
      selectAccount(selected.id, r.data);
      setShowDeposit(false); setAmount(''); setDescription('');
    } catch (e) {
      showAlert('error', e.response?.data?.error || 'Deposit failed');
    } finally { setActionLoading(false); }
  };

  const handleWithdraw = async () => {
    if (!amount || isNaN(amount) || +amount <= 0) return;
    setActionLoading(true);
    try {
      await transactionsAPI.withdraw({ account_id: selected.id, amount: parseFloat(amount), description });
      showAlert('success', `$${amount} withdrawn successfully!`);
      const r = await accountsAPI.list();
      setAccounts(r.data);
      selectAccount(selected.id, r.data);
      setShowWithdraw(false); setAmount(''); setDescription('');
    } catch (e) {
      showAlert('error', e.response?.data?.error || 'Withdrawal failed');
    } finally { setActionLoading(false); }
  };

  const handleCreate = async () => {
    setActionLoading(true);
    try {
      await accountsAPI.create({ account_type: newAccType, currency: newAccCurrency });
      showAlert('success', 'New account created!');
      const r = await accountsAPI.list();
      setAccounts(r.data);
      setShowCreate(false);
    } catch (e) {
      showAlert('error', 'Failed to create account');
    } finally { setActionLoading(false); }
  };

  if (loading) return <div className="loading-screen"><div className="spinner dark"></div><span>Loading accounts…</span></div>;

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
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
          <i className="bi bi-plus-lg"></i> New Account
        </button>
      </div>

      {/* Account Cards Row */}
      <div style={{ display: 'flex', gap: '1rem', overflowX: 'auto', paddingBottom: '0.5rem', marginBottom: '1.5rem' }}>
        {accounts.map((acc, i) => (
          <div
            key={acc.id}
            className={`bank-card ${ACCOUNT_COLORS[i % 3]}`}
            style={{ minWidth: 300, cursor: 'pointer', opacity: selected?.id === acc.id ? 1 : 0.75, transition: 'opacity 0.2s', outline: selected?.id === acc.id ? '3px solid white' : 'none', outlineOffset: 3 }}
            onClick={() => selectAccount(acc.id)}
          >
            <div className="bank-card-top">
              <div className="bank-card-chip"><i className="bi bi-sim-fill"></i></div>
              <div className="bank-card-network">{acc.account_type}</div>
            </div>
            <div className="bank-card-number">{acc.account_number.match(/.{1,4}/g)?.join('  ')}</div>
            <div className="bank-card-bottom">
              <div>
                <div className="bank-card-label">Balance</div>
                <div className="bank-card-value">{acc.currency} {parseFloat(acc.balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div className="bank-card-label">Status</div>
                <div className="bank-card-value">{acc.status}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {selected && (
        <div className="grid-2">
          {/* Account Details */}
          <div className="card">
            <div className="card-header">
              <div>
                <div className="card-title">Account Details</div>
                <div className="card-subtitle">{selected.account_number}</div>
              </div>
              <span className={`pill ${selected.status === 'ACTIVE' ? 'success' : 'neutral'}`}>{selected.status}</span>
            </div>
            <div>
              {[
                { label: 'Account Type', value: selected.account_type, icon: 'bi-wallet2' },
                { label: 'Currency', value: selected.currency, icon: 'bi-currency-dollar' },
                { label: 'Available Balance', value: `${selected.currency} ${parseFloat(selected.available_balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}`, icon: 'bi-cash-stack' },
                { label: 'Daily Limit', value: `${selected.currency} ${parseFloat(selected.daily_limit).toLocaleString()}`, icon: 'bi-arrow-repeat' },
                { label: 'Interest Rate', value: `${selected.interest_rate}% p.a.`, icon: 'bi-percent' },
              ].map(({ label, value, icon }) => (
                <div key={label} className="d-flex align-center justify-between" style={{ padding: '0.75rem 0', borderBottom: '1px solid var(--gray-50)' }}>
                  <div className="d-flex align-center gap-2 text-muted text-sm">
                    <i className={`bi ${icon}`}></i> {label}
                  </div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{value}</div>
                </div>
              ))}
            </div>
            <div className="d-flex gap-2 mt-4">
              <button className="btn btn-primary" style={{ flex: 1 }} onClick={() => { setShowDeposit(true); setAmount(''); setDescription(''); }}>
                <i className="bi bi-arrow-down-circle"></i> Deposit
              </button>
              <button className="btn btn-outline" style={{ flex: 1 }} onClick={() => { setShowWithdraw(true); setAmount(''); setDescription(''); }}>
                <i className="bi bi-arrow-up-circle"></i> Withdraw
              </button>
            </div>
          </div>

          {/* Transactions */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">Recent Transactions</div>
              <span className="text-muted text-sm">{txns.length} total</span>
            </div>
            {txnLoading ? (
              <div className="loading-screen" style={{ height: 150 }}><div className="spinner dark"></div></div>
            ) : txns.length === 0 ? (
              <div className="empty-state" style={{ padding: '2rem' }}>
                <i className="bi bi-arrow-left-right"></i>
                <h3>No transactions</h3>
                <p>Make a deposit to get started</p>
              </div>
            ) : (
              <div style={{ maxHeight: 380, overflowY: 'auto' }}>
                {txns.map(txn => (
                  <div key={txn.id} className="txn-item">
                    <div className={`txn-icon ${txn.transaction_type.toLowerCase()}`}>
                      <i className={`bi ${txn.transaction_type === 'DEPOSIT' ? 'bi-arrow-down-circle-fill' : txn.transaction_type === 'WITHDRAWAL' ? 'bi-arrow-up-circle-fill' : 'bi-arrow-left-right'}`}></i>
                    </div>
                    <div className="txn-info">
                      <div className="txn-name">{txn.description || txn.transaction_type}</div>
                      <div className="txn-date">{new Date(txn.created_at).toLocaleString()}</div>
                    </div>
                    <div className={`txn-amount ${txn.transaction_type === 'DEPOSIT' ? 'credit' : 'debit'}`}>
                      {txn.transaction_type === 'DEPOSIT' ? '+' : '-'}${parseFloat(txn.amount).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {accounts.length === 0 && (
        <div className="card">
          <div className="empty-state">
            <i className="bi bi-wallet2"></i>
            <h3>No accounts yet</h3>
            <p>Create your first bank account to get started</p>
            <button className="btn btn-primary mt-3" onClick={() => setShowCreate(true)}>
              <i className="bi bi-plus-lg"></i> Create Account
            </button>
          </div>
        </div>
      )}

      {/* Deposit Modal */}
      {showDeposit && (
        <div className="modal-overlay" onClick={() => setShowDeposit(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title"><i className="bi bi-arrow-down-circle" style={{ color: 'var(--success)', marginRight: 8 }}></i>Deposit Funds</div>
              <button className="modal-close" onClick={() => setShowDeposit(false)}><i className="bi bi-x"></i></button>
            </div>
            <div className="form-group">
              <label className="form-label">Amount ({selected?.currency})</label>
              <div className="input-group">
                <span className="input-prefix">$</span>
                <input className="form-control" type="number" placeholder="0.00" value={amount} onChange={e => setAmount(e.target.value)} min="1" step="0.01" />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Description (optional)</label>
              <input className="form-control" type="text" placeholder="e.g. Salary deposit" value={description} onChange={e => setDescription(e.target.value)} />
            </div>
            <div className="d-flex gap-2 mt-3">
              <button className="btn btn-ghost" style={{ flex: 1 }} onClick={() => setShowDeposit(false)}>Cancel</button>
              <button className="btn btn-primary" style={{ flex: 1 }} onClick={handleDeposit} disabled={actionLoading}>
                {actionLoading ? <><span className="spinner"></span> Processing…</> : <><i className="bi bi-check-lg"></i> Deposit</>}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Withdraw Modal */}
      {showWithdraw && (
        <div className="modal-overlay" onClick={() => setShowWithdraw(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title"><i className="bi bi-arrow-up-circle" style={{ color: 'var(--danger)', marginRight: 8 }}></i>Withdraw Funds</div>
              <button className="modal-close" onClick={() => setShowWithdraw(false)}><i className="bi bi-x"></i></button>
            </div>
            <div className="form-group">
              <label className="form-label">Amount ({selected?.currency})</label>
              <div className="input-group">
                <span className="input-prefix">$</span>
                <input className="form-control" type="number" placeholder="0.00" value={amount} onChange={e => setAmount(e.target.value)} min="1" step="0.01" />
              </div>
              <div className="form-hint">Available: {selected?.currency} {parseFloat(selected?.available_balance || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
            </div>
            <div className="form-group">
              <label className="form-label">Description (optional)</label>
              <input className="form-control" type="text" placeholder="e.g. ATM withdrawal" value={description} onChange={e => setDescription(e.target.value)} />
            </div>
            <div className="d-flex gap-2 mt-3">
              <button className="btn btn-ghost" style={{ flex: 1 }} onClick={() => setShowWithdraw(false)}>Cancel</button>
              <button className="btn btn-danger" style={{ flex: 1 }} onClick={handleWithdraw} disabled={actionLoading}>
                {actionLoading ? <><span className="spinner"></span> Processing…</> : <><i className="bi bi-check-lg"></i> Withdraw</>}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Account Modal */}
      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title"><i className="bi bi-plus-circle" style={{ color: 'var(--primary)', marginRight: 8 }}></i>Open New Account</div>
              <button className="modal-close" onClick={() => setShowCreate(false)}><i className="bi bi-x"></i></button>
            </div>
            <div className="form-group">
              <label className="form-label">Account Type</label>
              <select className="form-control" value={newAccType} onChange={e => setNewAccType(e.target.value)}>
                {['SAVINGS', 'CHECKING', 'BUSINESS', 'FIXED'].map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Currency</label>
              <select className="form-control" value={newAccCurrency} onChange={e => setNewAccCurrency(e.target.value)}>
                {['USD', 'EUR', 'GBP', 'KES', 'NGN'].map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div className="d-flex gap-2 mt-3">
              <button className="btn btn-ghost" style={{ flex: 1 }} onClick={() => setShowCreate(false)}>Cancel</button>
              <button className="btn btn-primary" style={{ flex: 1 }} onClick={handleCreate} disabled={actionLoading}>
                {actionLoading ? <><span className="spinner"></span> Creating…</> : <><i className="bi bi-check-lg"></i> Open Account</>}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Accounts;