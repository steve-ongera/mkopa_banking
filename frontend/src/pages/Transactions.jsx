import React, { useEffect, useState } from 'react';
import { transactionsAPI } from '../services/api';

const TX_ICONS = { DEPOSIT: 'bi-arrow-down-circle-fill', WITHDRAWAL: 'bi-arrow-up-circle-fill', TRANSFER: 'bi-arrow-left-right', PAYMENT: 'bi-receipt', REFUND: 'bi-arrow-counterclockwise', FEE: 'bi-dash-circle', INTEREST: 'bi-percent' };
const TX_COLOR = { DEPOSIT: 'deposit', WITHDRAWAL: 'withdrawal', TRANSFER: 'transfer', PAYMENT: 'payment', REFUND: 'transfer', FEE: 'withdrawal', INTEREST: 'deposit' };

const Transactions = () => {
  const [txns, setTxns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ type: '', start_date: '', end_date: '' });
  const [selected, setSelected] = useState(null);

  const load = () => {
    setLoading(true);
    const params = {};
    if (filter.type) params.type = filter.type;
    if (filter.start_date) params.start_date = filter.start_date;
    if (filter.end_date) params.end_date = filter.end_date;
    transactionsAPI.list(params).then(r => setTxns(r.data)).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  return (
    <div>
      {/* Filters */}
      <div className="card mb-4">
        <div className="d-flex gap-3 align-center" style={{ flexWrap: 'wrap' }}>
          <div style={{ flex: '1 1 150px' }}>
            <label className="form-label">Type</label>
            <select className="form-control" value={filter.type} onChange={e => setFilter(f => ({ ...f, type: e.target.value }))}>
              <option value="">All Types</option>
              {['DEPOSIT', 'WITHDRAWAL', 'TRANSFER', 'PAYMENT', 'REFUND'].map(t => <option key={t}>{t}</option>)}
            </select>
          </div>
          <div style={{ flex: '1 1 150px' }}>
            <label className="form-label">From Date</label>
            <input className="form-control" type="date" value={filter.start_date} onChange={e => setFilter(f => ({ ...f, start_date: e.target.value }))} />
          </div>
          <div style={{ flex: '1 1 150px' }}>
            <label className="form-label">To Date</label>
            <input className="form-control" type="date" value={filter.end_date} onChange={e => setFilter(f => ({ ...f, end_date: e.target.value }))} />
          </div>
          <div style={{ paddingTop: '1.5rem' }}>
            <button className="btn btn-primary" onClick={load}><i className="bi bi-search"></i> Filter</button>
          </div>
          <div style={{ paddingTop: '1.5rem' }}>
            <button className="btn btn-ghost" onClick={() => { setFilter({ type: '', start_date: '', end_date: '' }); setTimeout(load, 0); }}>Clear</button>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Transaction History</div>
            <div className="card-subtitle">{txns.length} transactions found</div>
          </div>
        </div>
        {loading ? (
          <div className="loading-screen"><div className="spinner dark"></div></div>
        ) : txns.length === 0 ? (
          <div className="empty-state"><i className="bi bi-arrow-left-right"></i><h3>No transactions found</h3><p>Try adjusting your filters</p></div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Transaction</th>
                  <th>Reference</th>
                  <th>Date</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {txns.map(txn => (
                  <tr key={txn.id}>
                    <td>
                      <div className="d-flex align-center gap-3">
                        <div className={`txn-icon ${TX_COLOR[txn.transaction_type] || 'transfer'}`} style={{ width: 36, height: 36, fontSize: '0.9rem', flexShrink: 0 }}>
                          <i className={`bi ${TX_ICONS[txn.transaction_type] || 'bi-arrow-left-right'}`}></i>
                        </div>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{txn.description || txn.transaction_type}</div>
                          <div className="text-muted" style={{ fontSize: '0.75rem' }}>{txn.transaction_type}</div>
                        </div>
                      </div>
                    </td>
                    <td><span className="font-mono text-sm">{txn.reference}</span></td>
                    <td className="text-sm text-muted">{new Date(txn.created_at).toLocaleString()}</td>
                    <td>
                      <span className={`txn-amount ${txn.transaction_type === 'DEPOSIT' || txn.transaction_type === 'REFUND' ? 'credit' : 'debit'}`}>
                        {txn.transaction_type === 'DEPOSIT' || txn.transaction_type === 'REFUND' ? '+' : '-'}${parseFloat(txn.amount).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                      </span>
                    </td>
                    <td>
                      <span className={`pill ${txn.status === 'COMPLETED' ? 'success' : txn.status === 'PENDING' ? 'warning' : 'danger'}`}>{txn.status}</span>
                    </td>
                    <td>
                      <button className="btn btn-ghost btn-sm" onClick={() => setSelected(txn)}><i className="bi bi-eye"></i></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selected && (
        <div className="modal-overlay" onClick={() => setSelected(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title">Transaction Details</div>
              <button className="modal-close" onClick={() => setSelected(null)}><i className="bi bi-x"></i></button>
            </div>
            <div className={`txn-icon ${TX_COLOR[selected.transaction_type]}`} style={{ margin: '0 auto 1.5rem', width: 56, height: 56, fontSize: '1.4rem' }}>
              <i className={`bi ${TX_ICONS[selected.transaction_type]}`}></i>
            </div>
            <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.8rem', fontWeight: 700 }}>
                ${parseFloat(selected.amount).toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </div>
              <span className={`pill ${selected.status === 'COMPLETED' ? 'success' : 'warning'}`}>{selected.status}</span>
            </div>
            {[
              { label: 'Reference', value: selected.reference, mono: true },
              { label: 'Type', value: selected.transaction_type },
              { label: 'Description', value: selected.description || '—' },
              { label: 'From', value: selected.from_account_number || '—' },
              { label: 'To', value: selected.to_account_number || '—' },
              { label: 'Fee', value: `$${parseFloat(selected.fee).toFixed(2)}` },
              { label: 'Balance After', value: `$${parseFloat(selected.balance_after).toLocaleString()}` },
              { label: 'Date', value: new Date(selected.created_at).toLocaleString() },
            ].map(({ label, value, mono }) => (
              <div key={label} className="d-flex justify-between" style={{ padding: '0.6rem 0', borderBottom: '1px solid var(--gray-50)' }}>
                <span className="text-muted text-sm">{label}</span>
                <span className={`${mono ? 'font-mono' : ''} fw-600 text-sm`}>{value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Transactions;