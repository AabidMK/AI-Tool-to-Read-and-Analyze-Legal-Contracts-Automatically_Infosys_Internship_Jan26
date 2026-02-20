import { ShieldCheck, FileSearch2, Download, Zap } from 'lucide-react';

export default function Hero() {
  return (
    <section style={styles.hero} className="animate-fade-in">
      <div style={styles.textBlock}>
        <div style={styles.badge}>
          <Zap size={12} />
          <span>AI-Powered Legal Intelligence</span>
        </div>
        <h2 style={styles.title}>Professional Contract Analysis</h2>
        <p style={styles.subtitle}>
          Upload legal documents and receive structured risk assessments, clause-level analysis,
          and expert recommendations powered by AI.
        </p>
      </div>
      <div style={styles.pills}>
        <Pill icon={<ShieldCheck size={13} />} label="Secure Analysis" />
        <Pill icon={<FileSearch2 size={13} />} label="Clause Intelligence" />
        <Pill icon={<Download size={13} />} label="Multi-Format Export" />
      </div>
    </section>
  );
}

function Pill({ icon, label }) {
  return (
    <span style={styles.pill}>
      {icon}
      {label}
    </span>
  );
}

const styles = {
  hero: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
    padding: '28px 32px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 24,
    position: 'relative',
    overflow: 'hidden',
  },
  textBlock: {
    flex: 1,
    minWidth: 0,
  },
  badge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
    background: 'var(--accent-muted)',
    color: 'var(--accent)',
    padding: '4px 12px',
    borderRadius: 'var(--radius-full)',
    fontSize: 11,
    fontWeight: 600,
    letterSpacing: '0.02em',
    marginBottom: 12,
  },
  title: {
    fontFamily: 'var(--font-serif)',
    fontSize: 26,
    fontWeight: 700,
    letterSpacing: '-0.02em',
    lineHeight: 1.2,
    marginBottom: 8,
    color: 'var(--text-primary)',
  },
  subtitle: {
    fontSize: 14,
    color: 'var(--text-secondary)',
    maxWidth: 520,
    lineHeight: 1.6,
  },
  pills: {
    display: 'flex',
    flexDirection: 'column',
    gap: 8,
    flexShrink: 0,
  },
  pill: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 8,
    border: '1px solid var(--border)',
    background: 'var(--bg-input)',
    borderRadius: 'var(--radius-full)',
    padding: '8px 16px',
    fontSize: 12,
    fontWeight: 500,
    color: 'var(--text-secondary)',
    transition: 'all 200ms',
    cursor: 'default',
    whiteSpace: 'nowrap',
  },
};
