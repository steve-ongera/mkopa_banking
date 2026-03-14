import React, { useState } from 'react';
import { useAuth } from '../components/AuthContext';
import { profileAPI } from '../services/api';

const Profile = () => {
  const { user, updateUser } = useAuth();
  const [form, setForm] = useState({ first_name: user?.first_name || '', last_name: user?.last_name || '', email: user?.email || '', phone: user?.phone || '', address: user?.address || '', city: user?.city || '', country: user?.country || '' });
  const [pwForm, setPwForm] = useState({ old_password: '', new_password: '' });
  const [saving, setSaving] = useState(false);
  const [changingPw, setChangingPw] = useState(false);
  const [alert, setAlert] = useState(null);
  const [pwAlert, setPwAlert] = useState(null);
  const [activeTab, setActiveTab] = useState('personal');

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }));
  const setPw = k => e => setPwForm(f => ({ ...f, [k]: e.target.value }));

  const showAlert = (setter, type, msg) => { setter({ type, msg }); setTimeout(() => setter(null), 5000); };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const { data } = await profileAPI.update(form);
      updateUser(data);
      showAlert(setAlert, 'success', 'Profile updated successfully!');
    } catch { showAlert(setAlert, 'error', 'Failed to update profile'); }
    finally { setSaving(false); }
  };

  const handlePwChange = async (e) => {
    e.preventDefault();
    setChangingPw(true);
    try {
      await profileAPI.changePassword(pwForm);
      showAlert(setPwAlert, 'success', 'Password changed successfully!');
      setPwForm({ old_password: '', new_password: '' });
    } catch (err) {
      showAlert(setPwAlert, 'error', err.response?.data?.error || 'Failed to change password');
    } finally { setChangingPw(false); }
  };

  const initials = ((user?.first_name?.[0] || '') + (user?.last_name?.[0] || '')) || user?.username?.[0]?.toUpperCase() || 'U';

  return (
    <div style={{ maxWidth: 700, margin: '0 auto' }}>
      {/* Profile Header */}
      <div className="card mb-4">
        <div className="d-flex align-center gap-4">
          <div style={{
            width: 80, height: 80, borderRadius: '50%',
            background: 'var(--primary-gradient)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'white', fontWeight: 800, fontSize: '1.8rem', flexShrink: 0,
            boxShadow: 'var(--shadow-blue)'
          }}>{initials}</div>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.3rem', fontWeight: 700 }}>
              {user?.first_name} {user?.last_name}
            </div>
            <div className="text-muted">@{user?.username} · {user?.email}</div>
            <div className="d-flex gap-2 mt-2">
              {user?.is_verified ? (
                <span className="pill success"><i className="bi bi-patch-check-fill"></i> Verified</span>
              ) : (
                <span className="pill warning"><i className="bi bi-clock"></i> Pending Verification</span>
              )}
              <span className="pill info"><i className="bi bi-person-fill"></i> Personal</span>
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div className="text-muted text-xs">Member since</div>
            <div style={{ fontWeight: 600 }}>{new Date(user?.created_at || Date.now()).toLocaleDateString('en-US', { year: 'numeric', month: 'long' })}</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.25rem', background: 'var(--gray-100)', borderRadius: 'var(--radius)', padding: '4px', marginBottom: '1.5rem' }}>
        {[
          { id: 'personal', label: 'Personal Info', icon: 'bi-person' },
          { id: 'security', label: 'Security', icon: 'bi-shield-lock' },
          { id: 'preferences', label: 'Preferences', icon: 'bi-gear' },
        ].map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)} className="btn btn-ghost" style={{
            flex: 1, borderRadius: 'var(--radius-sm)',
            background: activeTab === tab.id ? 'var(--white)' : 'transparent',
            color: activeTab === tab.id ? 'var(--primary)' : 'var(--gray-500)',
            fontWeight: activeTab === tab.id ? 700 : 500,
            boxShadow: activeTab === tab.id ? 'var(--shadow-sm)' : 'none',
          }}>
            <i className={`bi ${tab.icon}`}></i> {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'personal' && (
        <div className="card">
          <div className="card-header">
            <div className="card-title">Personal Information</div>
          </div>
          {alert && <div className={`alert ${alert.type}`}><i className={`bi ${alert.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill'}`}></i><span>{alert.msg}</span></div>}
          <form onSubmit={handleSave}>
            <div className="grid-2">
              {[
                { label: 'First Name', key: 'first_name', icon: 'bi-person' },
                { label: 'Last Name', key: 'last_name', icon: 'bi-person' },
              ].map(({ label, key, icon }) => (
                <div className="form-group" key={key}>
                  <label className="form-label">{label}</label>
                  <div className="input-group">
                    <i className={`bi ${icon} input-icon`}></i>
                    <input className="form-control" type="text" value={form[key]} onChange={set(key)} />
                  </div>
                </div>
              ))}
            </div>
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <div className="input-group">
                <i className="bi bi-envelope input-icon"></i>
                <input className="form-control" type="email" value={form.email} onChange={set('email')} />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Phone Number</label>
              <div className="input-group">
                <i className="bi bi-telephone input-icon"></i>
                <input className="form-control" type="tel" value={form.phone} onChange={set('phone')} placeholder="+1 234 567 8900" />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Address</label>
              <div className="input-group">
                <i className="bi bi-geo-alt input-icon"></i>
                <input className="form-control" type="text" value={form.address} onChange={set('address')} />
              </div>
            </div>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">City</label>
                <input className="form-control" type="text" value={form.city} onChange={set('city')} />
              </div>
              <div className="form-group">
                <label className="form-label">Country</label>
                <input className="form-control" type="text" value={form.country} onChange={set('country')} />
              </div>
            </div>
            <button className="btn btn-primary" type="submit" disabled={saving}>
              {saving ? <><span className="spinner"></span> Saving…</> : <><i className="bi bi-check-lg"></i> Save Changes</>}
            </button>
          </form>
        </div>
      )}

      {activeTab === 'security' && (
        <div className="card">
          <div className="card-header"><div className="card-title">Change Password</div></div>
          {pwAlert && <div className={`alert ${pwAlert.type}`}><i className={`bi ${pwAlert.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill'}`}></i><span>{pwAlert.msg}</span></div>}
          <form onSubmit={handlePwChange}>
            <div className="form-group">
              <label className="form-label">Current Password</label>
              <div className="input-group">
                <i className="bi bi-lock input-icon"></i>
                <input className="form-control" type="password" value={pwForm.old_password} onChange={setPw('old_password')} required />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">New Password</label>
              <div className="input-group">
                <i className="bi bi-lock-fill input-icon"></i>
                <input className="form-control" type="password" value={pwForm.new_password} onChange={setPw('new_password')} required />
              </div>
              <div className="form-hint">Minimum 8 characters with a mix of letters and numbers</div>
            </div>
            <button className="btn btn-primary" type="submit" disabled={changingPw}>
              {changingPw ? <><span className="spinner"></span> Updating…</> : <><i className="bi bi-shield-check"></i> Update Password</>}
            </button>
          </form>
          <div className="divider"></div>
          <div className="card-title mb-3">Security Settings</div>
          {[
            { label: '2-Factor Authentication', desc: 'Add an extra layer of security to your account', icon: 'bi-phone', enabled: user?.two_factor_enabled },
            { label: 'Login Notifications', desc: 'Get alerts for new sign-ins', icon: 'bi-bell', enabled: true },
            { label: 'Biometric Login', desc: 'Use fingerprint or face recognition', icon: 'bi-fingerprint', enabled: false },
          ].map(({ label, desc, icon, enabled }) => (
            <div key={label} className="d-flex align-center justify-between" style={{ padding: '0.85rem 0', borderBottom: '1px solid var(--gray-50)' }}>
              <div className="d-flex align-center gap-3">
                <div className="stat-icon blue" style={{ width: 36, height: 36, fontSize: '0.9rem' }}><i className={`bi ${icon}`}></i></div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{label}</div>
                  <div className="text-muted text-xs">{desc}</div>
                </div>
              </div>
              <div style={{
                width: 44, height: 24, borderRadius: 12,
                background: enabled ? 'var(--primary)' : 'var(--gray-200)',
                cursor: 'pointer', position: 'relative', transition: 'background 0.2s'
              }}>
                <div style={{
                  width: 18, height: 18, borderRadius: '50%', background: 'white',
                  position: 'absolute', top: 3, left: enabled ? 23 : 3,
                  transition: 'left 0.2s', boxShadow: '0 1px 3px rgba(0,0,0,0.2)'
                }}></div>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'preferences' && (
        <div className="card">
          <div className="card-header"><div className="card-title">Preferences</div></div>
          {[
            { label: 'Email Notifications', desc: 'Receive transaction alerts by email', enabled: true },
            { label: 'SMS Alerts', desc: 'Get SMS for every transaction', enabled: true },
            { label: 'Marketing Emails', desc: 'Receive promotional offers', enabled: false },
            { label: 'Statement Emails', desc: 'Monthly e-statements', enabled: true },
          ].map(({ label, desc, enabled }) => (
            <div key={label} className="d-flex align-center justify-between" style={{ padding: '0.85rem 0', borderBottom: '1px solid var(--gray-50)' }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{label}</div>
                <div className="text-muted text-xs">{desc}</div>
              </div>
              <div style={{ width: 44, height: 24, borderRadius: 12, background: enabled ? 'var(--primary)' : 'var(--gray-200)', cursor: 'pointer', position: 'relative' }}>
                <div style={{ width: 18, height: 18, borderRadius: '50%', background: 'white', position: 'absolute', top: 3, left: enabled ? 23 : 3, transition: 'left 0.2s', boxShadow: '0 1px 3px rgba(0,0,0,0.2)' }}></div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Profile;