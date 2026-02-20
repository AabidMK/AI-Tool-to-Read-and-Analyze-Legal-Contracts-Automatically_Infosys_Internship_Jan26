import { useState, useCallback, useRef } from 'react';
import { Upload, FileText, X, Sparkles } from 'lucide-react';
import { toast } from 'react-hot-toast';

export default function UploadPanel({ onUpload }) {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef(null);

  const validateFile = useCallback((f) => {
    const ext = f.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx'].includes(ext)) {
      toast.error('Only PDF and DOCX files are supported');
      return false;
    }
    if (f.size > 10 * 1024 * 1024) {
      toast.error('File too large (max 10 MB)');
      return false;
    }
    return true;
  }, []);

  const handleSelect = (f) => {
    if (validateFile(f)) setFile(f);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    if (e.dataTransfer.files.length) handleSelect(e.dataTransfer.files[0]);
  };

  const handleUpload = async () => {
    if (!file || uploading) return;
    setUploading(true);
    try {
      await onUpload(file);
    } finally {
      setUploading(false);
      setFile(null);
    }
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  };

  return (
    <div style={styles.card} className="animate-slide-up">
      <div style={styles.header}>
        <h3 style={styles.headerTitle}>Upload Contract</h3>
        <p style={styles.headerSub}>PDF or DOCX, up to 10 MB</p>
      </div>

      {!file ? (
        <div
          style={{
            ...styles.dropZone,
            borderColor: dragging ? 'var(--accent)' : 'var(--border-hover)',
            background: dragging ? 'var(--accent-muted)' : 'var(--bg-input)',
          }}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.docx"
            style={{ display: 'none' }}
            onChange={(e) => e.target.files.length && handleSelect(e.target.files[0])}
          />
          <div style={styles.uploadIconWrap}>
            <Upload size={22} />
          </div>
          <p style={styles.dropTitle}>Drag & drop your file here</p>
          <p style={styles.dropHint}>or click to browse from your device</p>
          <div style={styles.formatBadges}>
            <span style={styles.formatBadge}>PDF</span>
            <span style={styles.formatBadge}>DOCX</span>
          </div>
        </div>
      ) : (
        <div style={styles.filePreview}>
          <div style={styles.fileInfo}>
            <div style={styles.fileIcon}>
              <FileText size={18} />
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <p style={styles.fileName}>{file.name}</p>
              <p style={styles.fileSize}>{formatSize(file.size)}</p>
            </div>
            <button
              onClick={() => setFile(null)}
              style={styles.removeBtn}
              title="Remove file"
            >
              <X size={14} />
            </button>
          </div>
          <button
            onClick={handleUpload}
            disabled={uploading}
            style={{
              ...styles.uploadBtn,
              opacity: uploading ? 0.6 : 1,
              cursor: uploading ? 'not-allowed' : 'pointer',
            }}
          >
            <Sparkles size={16} />
            {uploading ? 'Starting...' : 'Start Analysis'}
          </button>
        </div>
      )}
    </div>
  );
}

const styles = {
  card: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
    padding: 24,
    transition: 'box-shadow 200ms',
  },
  header: {
    marginBottom: 16,
  },
  headerTitle: {
    fontSize: 16,
    fontWeight: 700,
    letterSpacing: '-0.01em',
  },
  headerSub: {
    fontSize: 13,
    color: 'var(--text-muted)',
    marginTop: 3,
  },
  dropZone: {
    border: '2px dashed',
    borderRadius: 'var(--radius)',
    textAlign: 'center',
    padding: '36px 24px',
    cursor: 'pointer',
    transition: 'all 200ms',
  },
  uploadIconWrap: {
    width: 52,
    height: 52,
    borderRadius: 'var(--radius)',
    margin: '0 auto 16px',
    background: 'linear-gradient(135deg, var(--accent), #8b5cf6)',
    color: '#fff',
    display: 'grid',
    placeItems: 'center',
    transition: 'transform 200ms',
  },
  dropTitle: {
    fontSize: 14,
    fontWeight: 600,
    marginBottom: 4,
    color: 'var(--text-primary)',
  },
  dropHint: {
    fontSize: 13,
    color: 'var(--text-muted)',
    marginBottom: 12,
  },
  formatBadges: {
    display: 'flex',
    gap: 6,
    justifyContent: 'center',
  },
  formatBadge: {
    padding: '3px 10px',
    borderRadius: 'var(--radius-full)',
    background: 'var(--bg-elevated)',
    border: '1px solid var(--border)',
    fontSize: 11,
    fontWeight: 600,
    color: 'var(--text-muted)',
    letterSpacing: '0.04em',
  },
  filePreview: {
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    background: 'var(--bg-input)',
    padding: 16,
    display: 'grid',
    gap: 14,
  },
  fileInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
  },
  fileIcon: {
    width: 40,
    height: 40,
    borderRadius: 'var(--radius-sm)',
    background: 'var(--accent-muted)',
    color: 'var(--accent)',
    display: 'grid',
    placeItems: 'center',
    flexShrink: 0,
  },
  fileName: {
    fontSize: 14,
    fontWeight: 600,
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    color: 'var(--text-primary)',
  },
  fileSize: {
    fontSize: 12,
    color: 'var(--text-muted)',
    marginTop: 1,
  },
  removeBtn: {
    width: 30,
    height: 30,
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-sm)',
    background: 'var(--bg-card)',
    color: 'var(--text-muted)',
    display: 'grid',
    placeItems: 'center',
    cursor: 'pointer',
    transition: 'all 200ms',
    flexShrink: 0,
  },
  uploadBtn: {
    width: '100%',
    height: 44,
    border: 'none',
    borderRadius: 'var(--radius-sm)',
    background: 'linear-gradient(135deg, var(--accent), #8b5cf6)',
    color: '#fff',
    fontSize: 14,
    fontWeight: 700,
    fontFamily: 'inherit',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    cursor: 'pointer',
    transition: 'all 200ms',
    boxShadow: '0 4px 14px rgba(99,102,241,0.3)',
  },
};
