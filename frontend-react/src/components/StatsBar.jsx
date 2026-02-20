import { AlertTriangle, ShieldCheck, ShieldAlert, TrendingUp } from 'lucide-react';

export default function StatsBar({ text }) {
  // Parse stats from report text
  const riskMatch = text.match(/Risk Level:\s*(High|Medium|Low)/i);
  const risk = riskMatch ? riskMatch[1] : 'Unknown';

  const missingCount = (text.match(/\[MISSING\/WEAK\]/g) || []).length;
  const presentCount = (text.match(/\[PRESENT\]/g) || []).length;
  const modCount = (text.match(/\*\*Modification \d+/g) || []).length;

  const riskColor = risk === 'High' ? 'var(--danger)' : risk === 'Medium' ? 'var(--warning)' : 'var(--success)';
  const riskBg = risk === 'High' ? 'var(--danger-muted)' : risk === 'Medium' ? 'var(--warning-muted)' : 'var(--success-muted)';

  return (
    <div style={styles.bar} className="animate-slide-up">
      <StatCard
        icon={<ShieldAlert size={18} style={{ color: riskColor }} />}
        label="Risk Level"
        value={risk}
        valueColor={riskColor}
        bg={riskBg}
      />
      <StatCard
        icon={<ShieldCheck size={18} style={{ color: 'var(--success)' }} />}
        label="Present Clauses"
        value={presentCount}
        valueColor="var(--success)"
        bg="var(--success-muted)"
      />
      <StatCard
        icon={<AlertTriangle size={18} style={{ color: 'var(--warning)' }} />}
        label="Missing/Weak"
        value={missingCount}
        valueColor="var(--warning)"
        bg="var(--warning-muted)"
      />
      <StatCard
        icon={<TrendingUp size={18} style={{ color: 'var(--info)' }} />}
        label="Modifications"
        value={modCount}
        valueColor="var(--info)"
        bg="var(--info-muted)"
      />
    </div>
  );
}

function StatCard({ icon, label, value, valueColor, bg }) {
  return (
    <div style={styles.card}>
      <div style={{ ...styles.iconWrap, background: bg }}>
        {icon}
      </div>
      <div>
        <p style={styles.label}>{label}</p>
        <p style={{ ...styles.value, color: valueColor }}>{value}</p>
      </div>
    </div>
  );
}

const styles = {
  bar: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: 12,
    marginTop: 20,
  },
  card: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: '14px 16px',
    display: 'flex',
    alignItems: 'center',
    gap: 12,
  },
  iconWrap: {
    width: 40,
    height: 40,
    borderRadius: 'var(--radius-sm)',
    display: 'grid',
    placeItems: 'center',
    flexShrink: 0,
  },
  label: {
    fontSize: 11,
    fontWeight: 500,
    color: 'var(--text-muted)',
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
  },
  value: {
    fontSize: 20,
    fontWeight: 800,
    letterSpacing: '-0.02em',
    marginTop: 1,
  },
};
