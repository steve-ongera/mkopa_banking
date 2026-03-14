import React, { useEffect, useState } from 'react';
import { beneficiariesAPI } from '../services/api';

export const Beneficiaries = () => {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ name: '', account_number: '', bank_name: '', nickname: '' });
  const [saving, setSaving] = useState(false);
  const [alert, setAlert] = useState(null);

  useEffect(() => { beneficiariesAPI.list().then(r => setList(r.data)).finally(() => setLoading(false)); }, []);

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }));

  const handleAdd = async () => {
    setSaving(true);
    try {
      const { data } = await beneficiariesAPI.create(form);
      setList(l => [data, ...l]);
      setAlert({ type: 'success', msg: 'Beneficiary added!' });
      setShowAdd(false);
      setForm({ name: '', account_number: '', bank_name: '', nickname: '' });
    } catch { setAlert({ type: 'error', msg: 'Failed to add beneficiary' }); }
    finally { setSaving(false); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Remove this beneficiary?')) return;
    await beneficiariesAPI.delete(id);
    setList(l => l.filter(b => b.id !== id));
  };

  const toggleFav = async (b) => {
    const { data } = await beneficiariesAPI.update(b.id, { is_favorite: !b.is_favorite });
    setList(l => l.map(x => x.id === b.id ? data : x));
  };

  if (loading) return <div className="loading-screen"><div className="spinner dark"></div></div>;

  return (
    <div>
      {alert && <div className={`alert ${alert.type}`}><i className={`bi ${alert.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill'}`}></i><span>{alert.msg}</span></div>}
      <div className="d-flex justify-between align-center mb-4">
        <div></div>
        <button className="btn btn-primary" onClick={() => setShowAdd(true)}><i className="bi bi-person-plus-fill"></i> Add Beneficiary</button>
      </div>

      {list.length === 0 ? (
        <div className="card"><div className="empty-state"><i className="bi bi-people"></i><h3>No beneficiaries</h3><p>Add saved payees for quick transfers</p></div></div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
          {list.sort((a, b) => b.is_favorite - a.is_favorite).map(b => (
            <div key={b.id} className="card">
              <div className="d-flex justify-between align-center mb-2">
                <div className="d-flex align-center gap-2">
                  <div className="user-avatar" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                    {b.name[0].toUpperCase()}
                  </div>
                  <div>
                    <div style={{ fontWeight: 700 }}>{b.name}</div>
                    {b.nickname && <div className="text-muted text-xs">{b.nickname}</div>}
                  </div>
                </div>
                <button className="btn btn-ghost btn-sm" onClick={() => toggleFav(b)} title={b.is_favorite ? 'Remove from favorites' : 'Add to favorites'}>
                  <i className={`bi ${b.is_favorite ? 'bi-star-fill' : 'bi-star'}`} style={{ color: b.is_favorite ? '#FFB300' : undefined }}></i>
                </button>
              </div>
              <div className="text-sm font-mono text-muted mb-1">{b.account_number}</div>
              {b.bank_name && <div className="text-xs text-muted"><i className="bi bi-bank2" style={{ marginRight: 4 }}></i>{b.bank_name}</div>}
              <div className="d-flex gap-2 mt-3">
                <button className="btn btn-outline btn-sm" style={{ flex: 1 }}><i className="bi bi-send"></i> Transfer</button>
                <button className="btn btn-ghost btn-sm" onClick={() => handleDelete(b.id)}><i className="bi bi-trash" style={{ color: 'var(--danger)' }}></i></button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showAdd && (
        <div className="modal-overlay" onClick={() => setShowAdd(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title">Add Beneficiary</div>
              <button className="modal-close" onClick={() => setShowAdd(false)}><i className="bi bi-x"></i></button>
            </div>
            {[
              { label: 'Full Name *', key: 'name', placeholder: 'John Doe', icon: 'bi-person' },
              { label: 'Account Number *', key: 'account_number', placeholder: '000000000000', icon: 'bi-hash' },
              { label: 'Bank Name', key: 'bank_name', placeholder: 'Optional', icon: 'bi-bank2' },
              { label: 'Nickname', key: 'nickname', placeholder: 'e.g. Mom, Landlord', icon: 'bi-tag' },
            ].map(({ label, key, placeholder, icon }) => (
              <div className="form-group" key={key}>
                <label className="form-label">{label}</label>
                <div className="input-group">
                  <i className={`bi ${icon} input-icon`}></i>
                  <input className="form-control" type="text" placeholder={placeholder} value={form[key]} onChange={set(key)} />
                </div>
              </div>
            ))}
            <div className="d-flex gap-2 mt-2">
              <button className="btn btn-ghost" style={{ flex: 1 }} onClick={() => setShowAdd(false)}>Cancel</button>
              <button className="btn btn-primary" style={{ flex: 1 }} onClick={handleAdd} disabled={saving || !form.name || !form.account_number}>
                {saving ? <><span className="spinner"></span> Saving…</> : <><i className="bi bi-check-lg"></i> Save</>}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Beneficiaries;