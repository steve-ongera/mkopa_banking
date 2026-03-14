import React, { useEffect, useState } from 'react';
import { cardsAPI } from '../services/api';

const NETWORK_COLORS = { VISA: '#1A1F6E', MASTERCARD: '#EB001B', AMEX: '#007BC1' };

const Cards = () => {
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(null);
  const [alert, setAlert] = useState(null);

  useEffect(() => {
    cardsAPI.list().then(r => setCards(r.data)).finally(() => setLoading(false));
  }, []);

  const showAlert = (type, msg) => { setAlert({ type, msg }); setTimeout(() => setAlert(null), 4000); };

  const toggleCard = async (id) => {
    setToggling(id);
    try {
      const { data } = await cardsAPI.toggle(id);
      setCards(cs => cs.map(c => c.id === id ? data : c));
      showAlert('success', `Card ${data.status === 'ACTIVE' ? 'activated' : 'blocked'} successfully`);
    } catch { showAlert('error', 'Failed to update card'); }
    finally { setToggling(null); }
  };

  if (loading) return <div className="loading-screen"><div className="spinner dark"></div></div>;

  return (
    <div>
      {alert && (
        <div className={`alert ${alert.type}`}>
          <i className={`bi ${alert.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill'}`}></i>
          <span>{alert.msg}</span>
        </div>
      )}

      {cards.length === 0 ? (
        <div className="card"><div className="empty-state"><i className="bi bi-credit-card-2-front"></i><h3>No cards found</h3><p>Cards linked to your accounts will appear here</p></div></div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
          {cards.map(card => (
            <div key={card.id} className="card" style={{ padding: 0, overflow: 'hidden' }}>
              {/* Visual Card */}
              <div style={{
                background: card.status === 'ACTIVE'
                  ? 'linear-gradient(135deg, #1A1F36 0%, #374151 100%)'
                  : 'linear-gradient(135deg, #9CA3AF 0%, #6B7280 100%)',
                padding: '1.5rem',
                color: 'white',
                position: 'relative',
                overflow: 'hidden',
              }}>
                <div style={{ position: 'absolute', top: -30, right: -30, width: 120, height: 120, borderRadius: '50%', background: 'rgba(255,255,255,0.06)' }}></div>
                <div style={{ position: 'absolute', bottom: -40, right: 20, width: 100, height: 100, borderRadius: '50%', background: 'rgba(255,255,255,0.04)' }}></div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                  <i className="bi bi-sim-fill" style={{ fontSize: '1.5rem', opacity: 0.8 }}></i>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                    <span style={{ fontSize: '0.75rem', opacity: 0.7, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{card.network}</span>
                    <span style={{ fontSize: '0.8rem', fontWeight: 700 }}>{card.card_type}</span>
                  </div>
                </div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', letterSpacing: '0.15em', marginBottom: '1.25rem', opacity: 0.9 }}>
                  {card.masked_number}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                  <div>
                    <div style={{ fontSize: '0.65rem', opacity: 0.6, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Card Holder</div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{card.card_holder_name}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.65rem', opacity: 0.6, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Expires</div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>
                      {String(card.expiry_month).padStart(2, '0')}/{String(card.expiry_year).slice(-2)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Card Info */}
              <div style={{ padding: '1.25rem' }}>
                <div className="d-flex justify-between align-center mb-3">
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{card.network} {card.card_type}</div>
                    <div className="text-muted text-sm">Linked to {card.account_number}</div>
                  </div>
                  <span className={`pill ${card.status === 'ACTIVE' ? 'success' : card.status === 'BLOCKED' ? 'danger' : 'warning'}`}>
                    {card.status}
                  </span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginBottom: '1rem' }}>
                  {[
                    { label: 'Spending Limit', value: `$${parseFloat(card.spending_limit).toLocaleString()}` },
                    { label: 'Contactless', value: card.contactless ? 'Enabled' : 'Disabled' },
                    { label: 'Online Payments', value: card.online_payments ? 'Enabled' : 'Disabled' },
                    { label: 'International', value: card.international_transactions ? 'Enabled' : 'Disabled' },
                  ].map(({ label, value }) => (
                    <div key={label} style={{ background: 'var(--gray-50)', borderRadius: 'var(--radius-sm)', padding: '0.6rem 0.75rem' }}>
                      <div style={{ fontSize: '0.7rem', color: 'var(--gray-500)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>{label}</div>
                      <div style={{ fontSize: '0.85rem', fontWeight: 600, marginTop: 2 }}>{value}</div>
                    </div>
                  ))}
                </div>

                <button
                  className={`btn ${card.status === 'ACTIVE' ? 'btn-danger' : 'btn-success'} btn-block`}
                  onClick={() => toggleCard(card.id)}
                  disabled={toggling === card.id}
                >
                  {toggling === card.id ? (
                    <><span className="spinner"></span> Processing…</>
                  ) : card.status === 'ACTIVE' ? (
                    <><i className="bi bi-lock-fill"></i> Block Card</>
                  ) : (
                    <><i className="bi bi-unlock-fill"></i> Activate Card</>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Cards;