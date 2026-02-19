const API_BASE = "";

async function uploadFile() {
  const fileInput = document.getElementById("fileInput");
  if (!fileInput.files.length) {
    alert("Please select a file.");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  document.getElementById("loading").classList.remove("hidden");
  document.getElementById("reportSection").classList.add("hidden");

  const response = await fetch(`/analyze`, {
    method: "POST",
    body: formData
  });

  const data = await response.json();
  pollResult(data.task_id);
}

async function pollResult(taskId) {
  const interval = setInterval(async () => {
    const response = await fetch(`/result/${taskId}`);
    const data = await response.json();

    if (data.status === "completed") {
      clearInterval(interval);
      document.getElementById("loading").classList.add("hidden");
      displayReport(data.result);
    }

    if (data.status === "failed") {
      clearInterval(interval);
      alert("Analysis failed.");
    }

  }, 3000);
}

function displayReport(result) {
  const report = result.final_report;

  let html = `
    <h3>Executive Summary</h3>
    <p>${report.executive_summary}</p>

    <h3>Overall Risk Level</h3>
    <p><strong>${report.overall_risk_level}</strong></p>

    <h3>Key Risks</h3>
    <ul>
      ${report.key_risks.map(r => `<li>${r}</li>`).join("")}
    </ul>

    <h3>Recommended Actions</h3>
    <ul>
      ${report.recommended_actions.map(r => `<li>${r}</li>`).join("")}
    </ul>
  `;

  document.getElementById("reportContent").innerHTML = html;
  document.getElementById("reportSection").classList.remove("hidden");
}

function downloadPDF() {
  const element = document.getElementById("reportContent");
  html2pdf().from(element).save("contract_report.pdf");
}
