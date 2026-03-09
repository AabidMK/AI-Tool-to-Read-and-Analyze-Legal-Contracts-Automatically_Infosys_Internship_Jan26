let taskId = null;

async function uploadFile() {

    const file = document.getElementById("fileInput").files[0];

    if (!file) {

        alert("Upload a file first");
        return;

    }

    const formData = new FormData();

    formData.append("file", file);

    document.getElementById("statusBox").innerText = "Uploading...";

    const response = await fetch("http://127.0.0.1:8000/analyze", {

        method: "POST",
        body: formData

    });

    const data = await response.json();

    taskId = data.task_id;

    document.getElementById("taskDisplay").innerText = "Task ID: " + taskId;

    document.getElementById("statusBox").innerText = "Processing...";

    pollResult();

}


async function pollResult() {

    if (!taskId) return;

    const interval = setInterval(async() => {

        const res = await fetch(`http://127.0.0.1:8000/result/${taskId}`);

        const data = await res.json();

        if (data.status === "completed") {

            clearInterval(interval);

            document.getElementById("statusBox").innerText = "Analysis Completed";

            displayResult(data);

        }

    }, 3000);

}


function displayResult(data) {

    if (data.report) {

        document.getElementById("finalReport").innerText = data.report;

    }

    if (data.vector_insights) {

        document.getElementById("vectorInsights").innerText = data.vector_insights;

    }

    if (data.role_analysis) {

        document.getElementById("roleAnalysis").innerText = data.role_analysis;

    }

}