import { useState, useCallback } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import UploadPanel from './components/UploadPanel';
import CapabilitiesPanel from './components/CapabilitiesPanel';
import ReportView from './components/ReportView';
import HistorySidebar from './components/HistorySidebar';
import StatsBar from './components/StatsBar';
import { uploadContract, getResult } from './api';
import { usePolling, useHealth } from './hooks/usePolling';

export default function App() {
  const [historyOpen, setHistoryOpen] = useState(false);
  const [currentTask, setCurrentTask] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [reportText, setReportText] = useState('');
  const [view, setView] = useState('upload'); // 'upload' | 'processing' | 'report'
  const isOnline = useHealth();

  const handleComplete = useCallback(async (data) => {
    try {
      const text = await getResult(data.task_id);
      setReportData(data);
      setReportText(text);
      setView('report');
      toast.success('Analysis complete!');
    } catch {
      toast.error('Error loading report');
      setView('upload');
    }
  }, []);

  const handleFail = useCallback((msg) => {
    toast.error(msg || 'Analysis failed');
    setView('upload');
  }, []);

  const polling = usePolling(currentTask, handleComplete, handleFail);

  const handleUpload = async (file) => {
    try {
      setView('processing');
      const data = await uploadContract(file);
      setCurrentTask(data.task_id);
      polling.start(data.task_id);
    } catch (e) {
      toast.error(e.message || 'Upload failed');
      setView('upload');
    }
  };

  const handleNewAnalysis = () => {
    polling.stop();
    setCurrentTask(null);
    setReportData(null);
    setReportText('');
    setView('upload');
  };

  const handleViewHistory = async (taskId, data) => {
    setHistoryOpen(false);
    if (data.status === 'completed') {
      try {
        const text = await getResult(taskId);
        setCurrentTask(taskId);
        setReportData(data);
        setReportText(text);
        setView('report');
      } catch {
        toast.error('Failed to load report');
      }
    } else if (data.status === 'processing' || data.status === 'pending') {
      setView('processing');
      setCurrentTask(taskId);
      polling.start(taskId);
      toast('Analysis in progress...', { icon: '⏳' });
    } else {
      toast.error('This analysis is not available');
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Toaster
        position="bottom-right"
        toastOptions={{
          className: 'toast-custom',
          duration: 3500,
          style: {
            background: '#1a1a1f',
            color: '#fafafa',
            border: '1px solid #27272a',
            fontSize: '13px',
          },
        }}
      />

      <Navbar
        isOnline={isOnline}
        onHistoryClick={() => setHistoryOpen(true)}
        onNewAnalysis={handleNewAnalysis}
        hasReport={view === 'report'}
      />

      <main style={{ flex: 1, padding: '24px 0 60px' }}>
        <div className="container">
          <Hero />

          {view === 'report' && reportData && (
            <StatsBar data={reportData} text={reportText} />
          )}

          <div className="workspace-grid">
            <div className="main-area">
              {view === 'upload' && (
                <UploadPanel onUpload={handleUpload} />
              )}
              {view === 'processing' && (
                <ProcessingView polling={polling} />
              )}
              {view === 'report' && reportData && (
                <ReportView
                  data={reportData}
                  text={reportText}
                  taskId={currentTask}
                  onNewAnalysis={handleNewAnalysis}
                />
              )}
            </div>

            {view === 'upload' && (
              <div className="side-area">
                <CapabilitiesPanel />
              </div>
            )}
          </div>
        </div>
      </main>

      <Footer />

      <HistorySidebar
        open={historyOpen}
        onClose={() => setHistoryOpen(false)}
        onSelect={handleViewHistory}
      />

      <style>{`
        .container {
          width: min(1200px, calc(100% - 48px));
          margin: 0 auto;
        }
        .workspace-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 20px;
          margin-top: 20px;
        }
        .workspace-grid:has(.side-area) {
          grid-template-columns: 1.2fr 0.8fr;
        }
        @media (max-width: 900px) {
          .workspace-grid, .workspace-grid:has(.side-area) {
            grid-template-columns: 1fr;
          }
          .container {
            width: calc(100% - 24px);
          }
        }
      `}</style>
    </div>
  );
}

function ProcessingView({ polling }) {
  const { progress, phase, elapsed } = polling;
  const mins = Math.floor(elapsed / 60);
  const secs = elapsed % 60;
  const timeStr = mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;

  return (
    <div className="animate-scale-in" style={styles.processingCard}>
      <div style={styles.processingHeader}>
        <div style={styles.spinnerWrap}>
          <svg style={styles.spinner} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M12 2a10 10 0 1 0 10 10" strokeLinecap="round" />
          </svg>
        </div>
        <div>
          <h3 style={styles.processingTitle}>Analyzing Contract</h3>
          <p style={styles.processingPhase}>{phase}</p>
        </div>
      </div>

      <div style={styles.progressOuter}>
        <div style={{ ...styles.progressInner, width: `${progress}%` }} />
      </div>

      <div style={styles.progressMeta}>
        <span style={styles.progressPct}>{Math.round(progress)}%</span>
        <span style={styles.progressTime}>{timeStr} elapsed</span>
      </div>

      <div style={styles.stepsGrid}>
        {['Extract text', 'Classify type', 'Find clauses', 'AI analysis', 'Risk review', 'Build report'].map((step, i) => {
          const stepPct = (i + 1) * 16;
          const done = progress >= stepPct;
          const active = !done && progress >= stepPct - 16;
          return (
            <div key={step} style={{
              ...styles.stepItem,
              opacity: done ? 1 : active ? 0.8 : 0.35,
              borderColor: done ? 'var(--success)' : active ? 'var(--accent)' : 'var(--border)',
            }}>
              <div style={{
                ...styles.stepDot,
                background: done ? 'var(--success)' : active ? 'var(--accent)' : 'var(--border)',
                boxShadow: active ? '0 0 8px var(--accent)' : 'none',
              }} />
              <span style={{ fontSize: 12, color: done ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                {step}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Footer() {
  return (
    <footer style={styles.footer}>
      <div className="container" style={styles.footerInner}>
        <span style={{ color: 'var(--text-dim)' }}>ClauseAI v1.0 — Enterprise Contract Review Platform</span>
        <span style={{ color: 'var(--text-dim)' }}>Powered by LangGraph + Qwen 2.5</span>
      </div>
    </footer>
  );
}

const styles = {
  processingCard: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
    padding: 32,
    display: 'grid',
    gap: 24,
  },
  processingHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: 16,
  },
  spinnerWrap: {
    width: 48,
    height: 48,
    borderRadius: 'var(--radius)',
    background: 'var(--accent-muted)',
    display: 'grid',
    placeItems: 'center',
    color: 'var(--accent)',
    flexShrink: 0,
  },
  spinner: {
    width: 24,
    height: 24,
    animation: 'spin 1s linear infinite',
  },
  processingTitle: {
    fontSize: 18,
    fontWeight: 700,
    margin: 0,
    letterSpacing: '-0.02em',
  },
  processingPhase: {
    fontSize: 13,
    color: 'var(--text-secondary)',
    marginTop: 2,
  },
  progressOuter: {
    width: '100%',
    height: 6,
    borderRadius: 'var(--radius-full)',
    background: 'var(--bg-elevated)',
    overflow: 'hidden',
  },
  progressInner: {
    height: '100%',
    borderRadius: 'var(--radius-full)',
    background: 'linear-gradient(90deg, var(--accent), var(--accent-hover))',
    transition: 'width 0.5s var(--ease)',
  },
  progressMeta: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: 12,
  },
  progressPct: {
    color: 'var(--accent)',
    fontWeight: 600,
    fontFamily: 'var(--font-mono)',
  },
  progressTime: {
    color: 'var(--text-muted)',
    fontFamily: 'var(--font-mono)',
  },
  stepsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: 10,
  },
  stepItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    padding: '8px 12px',
    borderRadius: 'var(--radius-sm)',
    border: '1px solid var(--border)',
    background: 'var(--bg-input)',
    transition: 'all 0.3s var(--ease)',
  },
  stepDot: {
    width: 7,
    height: 7,
    borderRadius: '50%',
    flexShrink: 0,
    transition: 'all 0.3s var(--ease)',
  },
  footer: {
    borderTop: '1px solid var(--border)',
    padding: '16px 0',
    marginTop: 'auto',
  },
  footerInner: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: 12,
  },
};
