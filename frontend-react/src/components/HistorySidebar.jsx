import { useState, useEffect } from 'react';
import { X, FileText, Trash2, Inbox, Clock } from 'lucide-react';
import { getHistory, deleteHistoryItem, getStatus } from '../api';
import { toast } from 'react-hot-toast';

export default function HistorySidebar({ open, onClose, onSelect }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) loadData();
  }, [open]);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await getHistory();
      setItems(data);
    } catch {
      toast.error('Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (e, taskId) => {
    e.stopPropagation();
    if (!confirm('Delete this analysis?')) return;
    try {
      await deleteHistoryItem(taskId);
      toast.success('Deleted');
      loadData();
    } catch {
      toast.error('Failed to delete');
    }
  };

  const handleSelect = async (item) => {
    try {
      const data = await getStatus(item.task_id);
      onSelect(item.task_id, data);
    } catch {
      toast.error('Failed to load');
    }
  };

  const formatDate = (iso) => {
    if (!iso) return '';
    try {
      const d = new Date(iso);
      const now = new Date();
      const diff = now - d;
      if (diff < 60000) return 'Just now';
      if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch { return ''; }
  };

  const statusColor = (status) => {
    if (status === 'completed') return 'var(--success)';
    if (status === 'failed') return 'var(--danger)';
    if (status === 'processing') return 'var(--accent)';
    return 'var(--text-muted)';
  };

  return (
    <>
      {/* Overlay */}
      {open && (
        <div
          style={styles.overlay}
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside style={{
        ...styles.sidebar,
        transform: open ? 'translateX(0)' : 'translateX(100%)',
      }}>
        <div style={styles.sidebarHeader}>
          <div>
            <h3 style={styles.sidebarTitle}>Recent Analyses</h3>
            <p style={styles.sidebarSub}>{items.length} total</p>
          </div>
          <button onClick={onClose} style={styles.closeBtn}>
            <X size={16} />
          </button>
        </div>

        <div style={styles.sidebarBody}>
          {loading ? (
            <div style={styles.emptyState}>
              <div className="animate-pulse" style={{ color: 'var(--text-muted)' }}>Loading...</div>
            </div>
          ) : items.length === 0 ? (
            <div style={styles.emptyState}>
              <Inbox size={32} style={{ color: 'var(--text-dim)' }} />
              <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>No analysis history yet</p>
            </div>
          ) : (
            <div style={styles.list}>
              {items.map((item) => (
                <div
                  key={item.task_id}
                  style={styles.item}
                  onClick={() => handleSelect(item)}
                >
                  <div style={styles.itemIcon}>
                    <FileText size={15} />
                  </div>
                  <div style={styles.itemContent}>
                    <p style={styles.itemTitle}>{item.file_name || 'Unknown'}</p>
                    <div style={styles.itemMeta}>
                      <span style={{
                        ...styles.statusDot,
                        background: statusColor(item.status),
                      }} />
                      <span>{item.contract_type || 'Pending'}</span>
                      <span>&bull;</span>
                      <Clock size={10} />
                      <span>{formatDate(item.created_at)}</span>
                    </div>
                  </div>
                  <button
                    onClick={(e) => handleDelete(e, item.task_id)}
                    style={styles.deleteBtn}
                    title="Delete"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </aside>
    </>
  );
}

const styles = {
  overlay: {
    position: 'fixed',
    inset: 0,
    background: 'rgba(0,0,0,0.5)',
    backdropFilter: 'blur(4px)',
    zIndex: 110,
    animation: 'fadeIn 0.2s ease',
  },
  sidebar: {
    position: 'fixed',
    top: 0,
    right: 0,
    width: 400,
    maxWidth: '90vw',
    height: '100vh',
    zIndex: 120,
    background: 'var(--bg-secondary)',
    borderLeft: '1px solid var(--border)',
    boxShadow: '-10px 0 40px rgba(0,0,0,0.4)',
    display: 'flex',
    flexDirection: 'column',
    transition: 'transform 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
  },
  sidebarHeader: {
    height: 64,
    padding: '0 20px',
    borderBottom: '1px solid var(--border)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexShrink: 0,
  },
  sidebarTitle: {
    fontSize: 15,
    fontWeight: 700,
  },
  sidebarSub: {
    fontSize: 11,
    color: 'var(--text-muted)',
    marginTop: 1,
  },
  closeBtn: {
    width: 32,
    height: 32,
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-sm)',
    background: 'var(--bg-card)',
    color: 'var(--text-muted)',
    display: 'grid',
    placeItems: 'center',
    cursor: 'pointer',
    transition: 'all 200ms',
  },
  sidebarBody: {
    flex: 1,
    overflow: 'auto',
    padding: 16,
  },
  emptyState: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    padding: '60px 0',
  },
  list: {
    display: 'grid',
    gap: 8,
  },
  item: {
    display: 'grid',
    gridTemplateColumns: 'auto 1fr auto',
    gap: 12,
    alignItems: 'center',
    padding: '12px 14px',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-sm)',
    background: 'var(--bg-card)',
    cursor: 'pointer',
    transition: 'all 200ms',
  },
  itemIcon: {
    width: 34,
    height: 34,
    borderRadius: 'var(--radius-sm)',
    background: 'var(--accent-muted)',
    color: 'var(--accent)',
    display: 'grid',
    placeItems: 'center',
    flexShrink: 0,
  },
  itemContent: {
    minWidth: 0,
  },
  itemTitle: {
    fontSize: 13,
    fontWeight: 600,
    wordBreak: 'break-word',
    color: 'var(--text-primary)',
  },
  itemMeta: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    fontSize: 11,
    color: 'var(--text-muted)',
    marginTop: 3,
  },
  statusDot: {
    width: 6,
    height: 6,
    borderRadius: '50%',
    flexShrink: 0,
  },
  deleteBtn: {
    width: 28,
    height: 28,
    border: 'none',
    borderRadius: 'var(--radius-sm)',
    background: 'transparent',
    color: 'var(--text-dim)',
    display: 'grid',
    placeItems: 'center',
    cursor: 'pointer',
    opacity: 0.5,
    transition: 'all 200ms',
  },
};
