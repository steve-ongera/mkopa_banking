import React, { useState } from 'react';
import { useAuth } from '../components/AuthContext';

const Register = ({ onSwitchToLogin }) => {
  const { register } = useAuth();
  const [form, setForm] = useState({
    username: '', email: '', first_name: '', last_name: '', phone: '', password: '', password2: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [showPw, setShowPw] = useState(false);

  const set = (key) => (e) => setForm(f => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    if (form.password !== form.password2) {
      setErrors({ password2: "Passwords don't match" });
      return;
    }
    setLoading(true);
    try {
      await register(form);
    } catch (err) {
      setErrors(err.response?.data || { general: 'Registration failed. Try again.' });
    } finally {
      setLoading(false);
    }
  };

  const Field = ({ label, name, type = 'text', placeholder, icon }) => (
    <div className="form-group">
      <label className="form-label">{label}</label>
      <div className="input-group">
        <i className={`bi ${icon} input-icon`}></i>
        <input
          className="form-control"
          type={name.includes('password') ? (showPw ? 'text' : 'password') : type}
          placeholder={placeholder}
          value={form[name]}
          onChange={set(name)}
          required
        />
      </div>
      {errors[name] && <div className="form-error">{Array.isArray(errors[name]) ? errors[name][0] : errors[name]}</div>}
    </div>
  );

  return (
    <div className="auth-page">
      <div className="auth-card" style={{ maxWidth: 500 }}>
        <div className="auth-logo">
          <div className="logo-icon"><i className="bi bi-shield-check"></i></div>
          <div className="logo-text">Nova<span>Pay</span></div>
        </div>

        <h1 className="auth-title">Create your account</h1>
        <p className="auth-subtitle">Start banking with NovaPay today</p>

        {errors.general && (
          <div className="alert error">
            <i className="bi bi-exclamation-circle-fill"></i>
            <span>{errors.general}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="grid-2">
            <Field label="First Name" name="first_name" placeholder="John" icon="bi-person" />
            <Field label="Last Name" name="last_name" placeholder="Doe" icon="bi-person" />
          </div>
          <Field label="Username" name="username" placeholder="johndoe" icon="bi-at" />
          <Field label="Email Address" name="email" type="email" placeholder="john@example.com" icon="bi-envelope" />
          <Field label="Phone Number" name="phone" type="tel" placeholder="+1 234 567 8900" icon="bi-telephone" />

          <div className="form-group">
            <label className="form-label">Password</label>
            <div className="input-group" style={{ position: 'relative' }}>
              <i className="bi bi-lock input-icon"></i>
              <input
                className="form-control"
                type={showPw ? 'text' : 'password'}
                placeholder="Min. 8 characters"
                value={form.password}
                onChange={set('password')}
                style={{ paddingRight: '2.5rem' }}
                required
              />
              <button type="button" onClick={() => setShowPw(s => !s)} style={{ position: 'absolute', right: '0.85rem', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--gray-500)', fontSize: '1rem' }}>
                <i className={`bi ${showPw ? 'bi-eye-slash' : 'bi-eye'}`}></i>
              </button>
            </div>
            {errors.password && <div className="form-error">{Array.isArray(errors.password) ? errors.password[0] : errors.password}</div>}
          </div>

          <div className="form-group">
            <label className="form-label">Confirm Password</label>
            <div className="input-group">
              <i className="bi bi-lock-fill input-icon"></i>
              <input
                className="form-control"
                type={showPw ? 'text' : 'password'}
                placeholder="Repeat your password"
                value={form.password2}
                onChange={set('password2')}
                required
              />
            </div>
            {errors.password2 && <div className="form-error">{errors.password2}</div>}
          </div>

          <div className="form-group">
            <label className="d-flex align-center gap-2" style={{ cursor: 'pointer', fontSize: '0.85rem', color: 'var(--gray-700)' }}>
              <input type="checkbox" required />
              I agree to the <a href="#terms" style={{ color: 'var(--primary)', fontWeight: 600 }}>Terms of Service</a> and <a href="#privacy" style={{ color: 'var(--primary)', fontWeight: 600 }}>Privacy Policy</a>
            </label>
          </div>

          <button className="btn btn-primary btn-block btn-lg" type="submit" disabled={loading}>
            {loading ? <><span className="spinner"></span> Creating account…</> : <><i className="bi bi-person-plus"></i> Create Account</>}
          </button>
        </form>

        <div className="auth-footer">
          Already have an account?{' '}
          <a href="#login" onClick={(e) => { e.preventDefault(); onSwitchToLogin(); }}>Sign in</a>
        </div>
      </div>
    </div>
  );
};

export default Register;