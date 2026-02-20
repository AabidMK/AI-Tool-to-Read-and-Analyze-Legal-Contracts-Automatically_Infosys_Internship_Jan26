const API_BASE = '';

export async function uploadContract(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/analyze`, { method: 'POST', body: formData });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Upload failed');
  }
  return res.json();
}

export async function getStatus(taskId) {
  const res = await fetch(`${API_BASE}/status/${taskId}`);
  if (!res.ok) throw new Error('Status check failed');
  return res.json();
}

export async function getResult(taskId) {
  const res = await fetch(`${API_BASE}/result/${taskId}`);
  if (!res.ok) throw new Error('Report not available');
  return res.text();
}

export async function getHistory() {
  const res = await fetch(`${API_BASE}/history`);
  if (!res.ok) throw new Error('Failed to load history');
  return res.json();
}

export async function deleteHistoryItem(taskId) {
  const res = await fetch(`${API_BASE}/history/${taskId}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete');
  return res.json();
}

export async function healthCheck() {
  const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(5000) });
  if (!res.ok) throw new Error('Unhealthy');
  return res.json();
}

export function getDownloadUrl(taskId, format = 'txt') {
  return `${API_BASE}/download/${taskId}?format=${format}`;
}
