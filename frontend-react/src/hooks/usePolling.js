import { useState, useEffect, useRef, useCallback } from 'react';
import { getStatus } from '../api';

export function usePolling(taskId, onComplete, onFail) {
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState('');
  const [elapsed, setElapsed] = useState(0);
  const [isPolling, setIsPolling] = useState(false);
  const intervalRef = useRef(null);
  const timerRef = useRef(null);
  const attemptsRef = useRef(0);

const PHASES = [
  'Uploading document...',
  'Extracting text from document...',
  'Classifying contract type...',
  'Identifying key clauses...',
  'Running AI agent analysis...',
  'Performing risk assessment...',
  'Generating comprehensive report...',
  'Finalizing analysis...',
];

  const stop = useCallback(() => {
    if (intervalRef.current) { clearInterval(intervalRef.current); intervalRef.current = null; }
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
    setIsPolling(false);
  }, []);

  const start = useCallback((id) => {
    stop();
    setIsPolling(true);
    setProgress(15);
    setPhase(PHASES[1]);
    setElapsed(0);
    attemptsRef.current = 0;

    timerRef.current = setInterval(() => {
      setElapsed(prev => prev + 1);
    }, 1000);

    intervalRef.current = setInterval(async () => {
      attemptsRef.current++;
      try {
        const data = await getStatus(id);
        if (data.status === 'completed') {
          setProgress(100);
          setPhase('Analysis complete!');
          stop();
          onComplete?.(data);
        } else if (data.status === 'failed') {
          stop();
          onFail?.(data.error || 'Analysis failed');
        } else {
          const pct = Math.min(15 + (attemptsRef.current * 5), 92);
          const phaseIdx = Math.min(Math.floor(attemptsRef.current / 3) + 1, PHASES.length - 1);
          setProgress(pct);
          setPhase(PHASES[phaseIdx]);
        }
      } catch (err) {
        console.error('Poll error:', err);
      }
    }, 3000);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stop, onComplete, onFail]);

  useEffect(() => {
    return () => stop();
  }, [stop]);

  return { progress, phase, elapsed, isPolling, start, stop };
}

export function useHealth() {
  const [online, setOnline] = useState(true);

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch('/health', { signal: AbortSignal.timeout(5000) });
        setOnline(res.ok);
      } catch {
        setOnline(false);
      }
    };
    check();
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, []);

  return online;
}
