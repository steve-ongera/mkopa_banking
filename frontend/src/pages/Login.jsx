import React, { useState } from 'react';
import { useAuth } from '../components/AuthContext';

const Login = ({ onSwitchToRegister }) => {
  const { login } = useAuth();
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPw, setShowPw] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(form);
    } catch (err) {
      setError(err.response?.data?.error || 'Invalid username or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="logo-icon"><i className="bi bi-shield-check"></i></div>
          <div className="logo-text">Nova<span>Pay</span></div>
        </div>

        <h1 className="auth-title">Welcome back</h1>
        <p className="auth-subtitle">Sign in to your banking account</p>

        {error && (
          <div className="alert error">
            <i className="bi bi-exclamation-circle-fill"></i>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <div className="input-group">
              <i className="bi bi-person input-icon"></i>
              <input
                className="form-control"
                type="text"
                placeholder="Enter your username"
                value={form.username}
                onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <div className="input-group" style={{ position: 'relative' }}>
              <i className="bi bi-lock input-icon"></i>
              <input
                className="form-control"
                type={showPw ? 'text' : 'password'}
                placeholder="Enter your password"
                value={form.password}
                onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                style={{ paddingRight: '2.5rem' }}
                required
              />
              <button
                type="button"
                onClick={() => setShowPw(s => !s)}
                style={{ position: 'absolute', right: '0.85rem', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--gray-500)', fontSize: '1rem' }}
              >
                <i className={`bi ${showPw ? 'bi-eye-slash' : 'bi-eye'}`}></i>
              </button>
            </div>
          </div>

          <div className="d-flex justify-between align-center mb-3">
            <label className="d-flex align-center gap-2" style={{ cursor: 'pointer', fontSize: '0.875rem', color: 'var(--gray-700)' }}>
              <input type="checkbox" /> Remember me
            </label>
            <a href="#forgot" style={{ fontSize: '0.875rem', color: 'var(--primary)', textDecoration: 'none', fontWeight: 600 }}>
              Forgot password?
            </a>
          </div>

          <button className="btn btn-primary btn-block btn-lg" type="submit" disabled={loading}>
            {loading ? <><span className="spinner"></span> Signing in…</> : <><i className="bi bi-box-arrow-in-right"></i> Sign In</>}
          </button>
        </form>

        <div className="auth-footer">
          Don't have an account?{' '}
          <a href="#register" onClick={(e) => { e.preventDefault(); onSwitchToRegister(); }}>
            Create account
          </a>
        </div>

        <div className="divider-text" style={{ marginTop: '1.5rem' }}>Secured by 256-bit SSL encryption</div>
        <div className="d-flex justify-between" style={{ gap: '0.5rem', marginTop: '0.5rem' }}>
          {['bi-shield-lock', 'bi-fingerprint', 'bi-bank'].map(icon => (
            <div key={icon} className="d-flex align-center gap-2 text-muted" style={{ fontSize: '0.75rem' }}>
              <i className={`bi ${icon}`} style={{ color: 'var(--primary)' }}></i>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Login;