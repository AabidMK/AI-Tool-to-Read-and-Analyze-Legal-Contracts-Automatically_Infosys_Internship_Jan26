import { Scale, Clock, Plus } from 'lucide-react';

export default function Navbar({ isOnline, onHistoryClick, onNewAnalysis, hasReport }) {
  return (
    <header style={styles.header}>
      <div className="container" style={styles.inner}>
        <div style={styles.brand}>
          <div style={styles.logo}>
            <Scale size={16} strokeWidth={2.5} />
          </div>
          <div>
            <h1 style={styles.title}>ClauseAI</h1>
            <p style={styles.subtitle}>Enterprise Contract Review</p>
          </div>
        </div>

        <div style={styles.actions}>
          {hasReport && (
            <button onClick={onNewAnalysis} style={styles.btnGhost}>
              <Plus size={14} />
              <span>New Analysis</span>
            </button>
          )}
          <button onClick={onHistoryClick} style={styles.btnSecondary}>
            <Clock size={14} />
            <span>History</span>
          </button>
          <div style={{
            ...styles.statusPill,
            borderColor: isOnline ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)',
          }}>
            <div style={{
              ...styles.statusDot,
              background: isOnline ? 'var(--success)' : 'var(--danger)',
              boxShadow: isOnline
                ? '0 0 6px rgba(34,197,94,0.4)'
                : '0 0 6px rgba(239,68,68,0.4)',
            }} />
            <span style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-secondary)' }}>
              {isOnline ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}

const styles = {
  header: {
    position: 'sticky',
    top: 0,
    zIndex: 100,
    background: 'rgba(9,9,11,0.85)',
    backdropFilter: 'blur(20px) saturate(180%)',
    WebkitBackdropFilter: 'blur(20px) saturate(180%)',
    borderBottom: '1px solid var(--border)',
  },
  inner: {
    height: 60,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  brand: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
  },
  logo: {
    width: 34,
    height: 34,
    borderRadius: 'var(--radius-sm)',
    background: 'linear-gradient(135deg, var(--accent), #8b5cf6)',
    display: 'grid',
    placeItems: 'center',
    color: '#fff',
    boxShadow: '0 2px 8px rgba(99,102,241,0.3)',
  },
  title: {
    fontSize: 16,
    fontWeight: 800,
    letterSpacing: '-0.04em',
    lineHeight: 1.1,
    color: 'var(--text-primary)',
  },
  subtitle: {
    fontSize: 11,
    fontWeight: 500,
    color: 'var(--text-muted)',
    letterSpacing: '0.02em',
  },
  actions: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  },
  btnSecondary: {
    height: 34,
    padding: '0 14px',
    borderRadius: 'var(--radius-sm)',
    border: '1px solid var(--border)',
    background: 'var(--bg-card)',
    color: 'var(--text-secondary)',
    fontSize: 13,
    fontWeight: 600,
    fontFamily: 'inherit',
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
    cursor: 'pointer',
    transition: 'all 200ms',
  },
  btnGhost: {
    height: 34,
    padding: '0 14px',
    borderRadius: 'var(--radius-sm)',
    border: '1px solid transparent',
    background: 'transparent',
    color: 'var(--accent)',
    fontSize: 13,
    fontWeight: 600,
    fontFamily: 'inherit',
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
    cursor: 'pointer',
    transition: 'all 200ms',
  },
  statusPill: {
    height: 30,
    padding: '0 10px',
    borderRadius: 'var(--radius-full)',
    border: '1px solid',
    background: 'var(--bg-card)',
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
  },
  statusDot: {
    width: 7,
    height: 7,
    borderRadius: '50%',
    transition: 'all 300ms',
  },
};
