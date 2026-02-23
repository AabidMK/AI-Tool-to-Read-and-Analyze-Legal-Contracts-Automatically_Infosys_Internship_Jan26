const API_BASE = 'http://localhost:8000';
let currentTaskId = null;
let currentReport = null;

// Check API health on load
async function checkAPIHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    const status = document.getElementById('apiStatus');
    if (response.ok) {
      status.className = 'service-dot';
    } else {
      status.className = 'service-dot warn';
    }
  } catch (error) {
    document.getElementById('apiStatus').className = 'service-dot off';
  }
}

checkAPIHealth();

// File handling
function handleDrop(e) {
  e.preventDefault();
  document.getElementById('uploadZone').classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file && file.type === 'application/pdf') processFile(file);
}

function handleFile(e) {
  const file = e.target.files[0];
  if (file) processFile(file);
}

async function processFile(file) {
  const zone = document.getElementById('uploadZone');
  zone.innerHTML = `<span class="upload-icon">📄</span>
    <div class="upload-title">${file.name}</div>
    <div class="upload-sub">Uploading... <span class="spinner"></span></div>`;
  zone.style.borderColor = 'var(--accent)';
  zone.style.background = 'rgba(124,109,255,0.05)';
  zone.onclick = null;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) throw new Error('Upload failed');

    const data = await response.json();
    currentTaskId = data.task_id;

    zone.innerHTML = `<span class="upload-icon">⏳</span>
      <div class="upload-title">Processing...</div>
      <div class="upload-sub">Task ID: ${currentTaskId.substring(0, 8)}... <span class="spinner"></span></div>`;

    pollResult();
  } catch (error) {
    zone.innerHTML = `<span class="upload-icon">❌</span>
      <div class="upload-title">Upload Failed</div>
      <div class="upload-sub" style="color: var(--danger);">${error.message}</div>`;
    zone.onclick = () => document.getElementById('fileInput').click();
  }
}

function updatePipelineStep(step) {
  const steps = ['step1', 'step2', 'step3', 'step4', 'step5'];
  const stepIndex = step - 1;
  
  // Mark all previous steps as done
  for (let i = 0; i < stepIndex; i++) {
    document.getElementById(steps[i]).classList.remove('active');
    document.getElementById(steps[i]).classList.add('done');
  }
  
  // Mark current step as active
  if (stepIndex < steps.length) {
    document.getElementById(steps[stepIndex]).classList.remove('done');
    document.getElementById(steps[stepIndex]).classList.add('active');
  }
}

async function pollResult() {
  const maxAttempts = 60;
  let attempts = 0;

  const poll = async () => {
    if (attempts >= maxAttempts) {
      showError('Processing timeout');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/result/${currentTaskId}`);
      const data = await response.json();

      console.log('Poll attempt', attempts, 'Status:', data.status, 'Data:', data);

      // Update pipeline based on status
      if (data.status === 'processing') {
        if (attempts < 3) updatePipelineStep(2);
        else if (attempts < 6) updatePipelineStep(3);
        else if (attempts < 10) updatePipelineStep(4);
        else updatePipelineStep(5);
      }

      if (data.status === 'completed') {
        console.log('Report received:', data.report);
        updatePipelineStep(5);
        setTimeout(() => {
          document.getElementById('step5').classList.remove('active');
          document.getElementById('step5').classList.add('done');
        }, 500);
        currentReport = data.report;
        setTimeout(() => showResults(), 800);
      } else if (data.status === 'failed') {
        showError(data.error || 'Processing failed');
      } else {
        attempts++;
        setTimeout(poll, 2000);
      }
    } catch (error) {
      console.error('Poll error:', error);
      showError('Failed to fetch results: ' + error.message);
    }
  };

  updatePipelineStep(1);
  setTimeout(() => {
    updatePipelineStep(2);
    poll();
  }, 1000);
}

function showResults() {
  const zone = document.getElementById('uploadZone');
  zone.innerHTML = `<span class="upload-icon">✓</span>
    <div class="upload-title">Analysis Complete</div>
    <div class="upload-sub" style="color: var(--accent2);">Report generated successfully</div>`;
  zone.style.borderColor = 'var(--accent2)';
  zone.style.background = 'rgba(56,217,169,0.05)';
  zone.style.padding = '24px';

  document.getElementById('resultsArea').style.display = 'block';

  renderSummary();
  renderAnalyses();
}

function renderSummary() {
  const summary = currentReport.contract_summary || {};
  const findings = currentReport.consolidated_findings || {};
  const execSummary = currentReport.executive_summary || 'No executive summary available';

  console.log('Rendering summary:', { summary, findings, execSummary });

  const html = `
    <div class="contract-type">
      <span>contract_type</span>
      ${summary.type || 'Unknown'}
    </div>
    <div style="margin-top: 10px;">
      <span class="tag tag-industry">${summary.industry || 'Unknown'}</span>
      <span class="tag tag-risk">${summary.overall_risk_rating || 'Unknown'}</span>
    </div>

    <div style="margin-top: 16px; padding: 12px; background: var(--surface2); border-radius: 6px; border: 1px solid var(--border);">
      <div style="font-size: 9px; text-transform: uppercase; letter-spacing: 1.5px; color: var(--muted); margin-bottom: 8px;">Executive Summary</div>
      <div style="font-size: 11px; line-height: 1.7; color: var(--text);">${execSummary}</div>
    </div>

    <div class="meta-rows">
      <div class="meta-row">
        <span class="meta-key">task_id</span>
        <span class="meta-val" style="font-size:10px; color: var(--accent);">${currentTaskId.substring(0, 16)}...</span>
      </div>
      <div class="meta-row">
        <span class="meta-key">total_risks</span>
        <span class="meta-val" style="color: var(--danger);">${findings.total_risks_identified || 0}</span>
      </div>
      <div class="meta-row">
        <span class="meta-key">compliance_issues</span>
        <span class="meta-val" style="color: var(--accent3);">${findings.critical_compliance_issues || 0}</span>
      </div>
      <div class="meta-row">
        <span class="meta-key">recommendations</span>
        <span class="meta-val" style="color: var(--accent2);">${(findings.key_recommendations || []).length}</span>
      </div>
      <div class="meta-row">
        <span class="meta-key">expert_analyses</span>
        <span class="meta-val">${(currentReport.expert_analyses || []).length}</span>
      </div>
    </div>
  `;

  document.getElementById('summaryBody').innerHTML = html;
}

function renderAnalyses() {
  const analyses = currentReport.expert_analyses || [];
  const list = document.getElementById('analysesList');
  list.innerHTML = '';

  console.log('Rendering analyses:', analyses);

  if (analyses.length === 0) {
    list.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--muted);">No expert analyses available</div>';
    return;
  }

  analyses.forEach((analysis, idx) => {
    const div = document.createElement('div');
    div.className = 'clause-card';
    div.style.animationDelay = `${idx * 0.08}s`;
    div.style.opacity = '0';
    div.style.animation = `fade-up 0.4s ${idx * 0.08}s ease forwards`;

    const findingsCount = (analysis.key_findings || []).length;
    const risksCount = (analysis.risks || []).length;
    const recsCount = (analysis.recommendations || []).length;
    const preview = (analysis.key_findings || [])[0] || 'Click to view details';

    div.innerHTML = `
      <div class="clause-title-text">${analysis.role || 'Expert'}</div>
      <div class="clause-preview">${preview}</div>
      <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
        <span class="score-badge score-mid">${analysis.rating || 'N/A'}</span>
        <span style="font-size: 10px; color: var(--muted);">
          ${findingsCount} findings · ${risksCount} risks · ${recsCount} recommendations
        </span>
      </div>
    `;

    div.onclick = () => openDrawer(analysis, idx);
    list.appendChild(div);
  });
}

function openDrawer(analysis, idx) {
  document.getElementById('drawerTitle').textContent = analysis.role || 'Expert Analysis';

  const findings = (analysis.key_findings || []).map(f => `<li>${f}</li>`).join('');
  const risks = (analysis.risks || []).map(r => `<li>${r}</li>`).join('');
  const recommendations = (analysis.recommendations || []).map(r => `<li>${r}</li>`).join('');

  document.getElementById('drawerBody').innerHTML = `
    <div style="margin-bottom: 16px;">
      <span class="score-badge score-mid">${analysis.rating || 'N/A'}</span>
    </div>

    ${findings ? `
      <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; color: var(--muted); margin-bottom: 8px;">Key Findings</div>
      <ul style="font-size: 11px; line-height: 1.8; color: var(--text); margin-bottom: 20px; padding-left: 20px;">${findings}</ul>
    ` : ''}

    ${risks ? `
      <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; color: var(--muted); margin-bottom: 8px;">Risks</div>
      <ul style="font-size: 11px; line-height: 1.8; color: var(--danger); margin-bottom: 20px; padding-left: 20px;">${risks}</ul>
    ` : ''}

    ${recommendations ? `
      <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; color: var(--muted); margin-bottom: 8px;">Recommendations</div>
      <ul style="font-size: 11px; line-height: 1.8; color: var(--accent2); margin-bottom: 20px; padding-left: 20px;">${recommendations}</ul>
    ` : ''}
  `;

  document.getElementById('drawer').classList.add('open');
  document.getElementById('overlay').classList.add('active');
}

function closeDrawer() {
  document.getElementById('drawer').classList.remove('open');
  document.getElementById('overlay').classList.remove('active');
}

async function downloadReport() {
  if (!currentTaskId) return;

  try {
    const response = await fetch(`${API_BASE}/download/${currentTaskId}`);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `contract_report_${currentTaskId.substring(0, 8)}.md`;
    a.click();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    alert('Failed to download report');
  }
}

function showError(message) {
  const zone = document.getElementById('uploadZone');
  zone.innerHTML = `<span class="upload-icon">❌</span>
    <div class="upload-title">Error</div>
    <div class="upload-sub" style="color: var(--danger);">${message}</div>`;
  zone.style.borderColor = 'var(--danger)';
  zone.style.background = 'rgba(255,92,106,0.05)';
  zone.onclick = () => document.getElementById('fileInput').click();
}

function resetUI() {
  location.reload();
}
