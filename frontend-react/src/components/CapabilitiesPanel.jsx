import { CheckCircle2, Shield, Brain, FileSearch, Users, Wrench } from 'lucide-react';

const capabilities = [
  { icon: <FileSearch size={15} />, label: 'Contract type & industry classification' },
  { icon: <Shield size={15} />, label: 'Clause-level gap & risk identification' },
  { icon: <Users size={15} />, label: 'Multi-role legal perspective review' },
  { icon: <Brain size={15} />, label: 'AI-powered risk assessment engine' },
  { icon: <Wrench size={15} />, label: 'Actionable recommendations & edits' },
  { icon: <CheckCircle2 size={15} />, label: 'Export as PDF, DOCX, or text' },
];

export default function CapabilitiesPanel() {
  return (
    <div style={styles.card} className="animate-slide-up">
      <div style={styles.header}>
        <h3 style={styles.title}>What We Analyze</h3>
        <p style={styles.subtitle}>Built for legal and business teams</p>
      </div>
      <div style={styles.list} className="stagger">
        {capabilities.map((cap, i) => (
          <div key={i} style={styles.item}>
            <div style={styles.itemIcon}>{cap.icon}</div>
            <span style={styles.itemLabel}>{cap.label}</span>
          </div>
        ))}
      </div>

      <div style={styles.trustBar}>
        <div style={styles.trustItem}>
          <span style={styles.trustNumber}>10+</span>
          <span style={styles.trustLabel}>Clause Types</span>
        </div>
        <div style={styles.divider} />
        <div style={styles.trustItem}>
          <span style={styles.trustNumber}>2+</span>
          <span style={styles.trustLabel}>Expert Roles</span>
        </div>
        <div style={styles.divider} />
        <div style={styles.trustItem}>
          <span style={styles.trustNumber}>3</span>
          <span style={styles.trustLabel}>Export Formats</span>
        </div>
      </div>
    </div>
  );
}

const styles = {
  card: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
    padding: 24,
  },
  header: {
    marginBottom: 16,
  },
  title: {
    fontSize: 16,
    fontWeight: 700,
    letterSpacing: '-0.01em',
  },
  subtitle: {
    fontSize: 13,
    color: 'var(--text-muted)',
    marginTop: 3,
  },
  list: {
    display: 'grid',
    gap: 8,
    marginBottom: 20,
  },
  item: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    padding: '11px 14px',
    borderRadius: 'var(--radius-sm)',
    border: '1px solid var(--border)',
    background: 'var(--bg-input)',
    transition: 'all 200ms',
    cursor: 'default',
  },
  itemIcon: {
    color: 'var(--accent)',
    flexShrink: 0,
    display: 'flex',
  },
  itemLabel: {
    fontSize: 13,
    fontWeight: 500,
    color: 'var(--text-secondary)',
  },
  trustBar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-around',
    padding: '14px 0',
    borderTop: '1px solid var(--border)',
    borderBottom: '1px solid var(--border)',
    borderRadius: 0,
  },
  trustItem: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 2,
  },
  trustNumber: {
    fontSize: 20,
    fontWeight: 800,
    color: 'var(--accent)',
    letterSpacing: '-0.02em',
  },
  trustLabel: {
    fontSize: 11,
    fontWeight: 500,
    color: 'var(--text-muted)',
  },
  divider: {
    width: 1,
    height: 32,
    background: 'var(--border)',
  },
};
