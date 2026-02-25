const { useState, useRef, useEffect } = React;

// CONFIGURE YOUR BACKEND URL HERE
const API_BASE_URL = 'http://localhost:8000';

function App() {
    const [file, setFile] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [progress, setProgress] = useState(0);
    const [result, setResult] = useState(null);
    const [taskId, setTaskId] = useState(null);
    const [statusInfo, setStatusInfo] = useState(null);
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef(null);
    const pollingIntervalRef = useRef(null);

    // Poll status endpoint
    const pollStatus = async (id) => {
        try {
            const response = await fetch(`${API_BASE_URL}/status/${id}`);
            if (!response.ok) {
                throw new Error('Failed to fetch status');
            }
            
            const data = await response.json();
            setStatusInfo(data);

            // Update progress based on status
            if (data.status === 'pending') {
                setProgress(25);
            } else if (data.status === 'processing') {
                setProgress(50);
            } else if (data.status === 'completed') {
                setProgress(100);
                // Stop polling
                if (pollingIntervalRef.current) {
                    clearInterval(pollingIntervalRef.current);
                    pollingIntervalRef.current = null;
                }
                // Fetch the final report
                await fetchReport(id);
            } else if (data.status === 'failed') {
                setProgress(0);
                setIsProcessing(false);
                if (pollingIntervalRef.current) {
                    clearInterval(pollingIntervalRef.current);
                    pollingIntervalRef.current = null;
                }
                alert(`Analysis failed: ${data.error || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Polling error:', error);
        }
    };

    // Fetch the final report
    const fetchReport = async (id) => {
        try {
            const response = await fetch(`${API_BASE_URL}/result/${id}`);
            if (!response.ok) {
                throw new Error('Failed to fetch report');
            }
            
            const reportText = await response.text();
            setResult({
                task_id: id,
                report: reportText,
                contract_type: statusInfo?.contract_type,
                industry: statusInfo?.industry
            });
            setIsProcessing(false);
        } catch (error) {
            console.error('Error fetching report:', error);
            alert('Failed to fetch the analysis report');
            setIsProcessing(false);
        }
    };

    // Cleanup polling on unmount
    useEffect(() => {
        return () => {
            if (pollingIntervalRef.current) {
                clearInterval(pollingIntervalRef.current);
            }
        };
    }, []);

    const handleFileSelect = (selectedFile) => {
        if (selectedFile && (selectedFile.type === 'application/pdf' || selectedFile.name.endsWith('.pdf') || selectedFile.name.endsWith('.docx'))) {
            setFile(selectedFile);
            setResult(null);
            setStatusInfo(null);
            setTaskId(null);
        } else {
            alert('Please upload a PDF or DOCX file');
        }
    };

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        handleFileSelect(selectedFile);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        const droppedFile = e.dataTransfer.files[0];
        handleFileSelect(droppedFile);
    };

    const handleAnalyze = async () => {
        if (!file) return;

        setIsProcessing(true);
        setProgress(10);
        setResult(null);
        setStatusInfo(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            // Call FastAPI /analyze endpoint
            const response = await fetch(`${API_BASE_URL}/analyze`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || 'Analysis failed');
            }

            const data = await response.json();
            setTaskId(data.task_id);

            // Start polling for status
            pollingIntervalRef.current = setInterval(() => {
                pollStatus(data.task_id);
            }, 2000); // Poll every 2 seconds

            // Initial poll
            pollStatus(data.task_id);

        } catch (error) {
            console.error('Error:', error);
            alert(`Failed to analyze contract: ${error.message}`);
            setIsProcessing(false);
            setProgress(0);
        }
    };

    const handleDownload = async () => {
        if (!taskId) return;
        
        try {
            // Download the report file
            const response = await fetch(`${API_BASE_URL}/result/${taskId}`);
            if (!response.ok) {
                throw new Error('Failed to download report');
            }
            
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `contract_analysis_${taskId}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Download error:', error);
            alert('Failed to download report');
        }
    };

    const circumference = 2 * Math.PI * 72;
    const strokeDashoffset = circumference - (progress / 100) * circumference;

    return (
        <div className="container">
            <header className="header">
                <div className="logo">
                    <div className="logo-icon">AI</div>
                    AI Contract Analyzer
                </div>
                <nav className="nav">
                    <a href="#help">Help</a>
                    <a href="#about">About</a>
                    <div className="nav-buttons">
                        <button className="btn-contact">Contact Us</button>
                    </div>
                </nav>
            </header>

            <div className="main-content">
                <div className="left-section">
                    <div className="subtitle">AI-Powered Multi-Agent System</div>
                    <h1 className="title">Automate Contract Analysis</h1>
                    <p className="description">
                        Leverage advanced AI technology to analyze legal contracts with precision. Our multi-agent framework specializes in compliance, finance, and operations to deliver comprehensive, actionable insights in minutes.
                    </p>
                    <button className="btn-start" onClick={() => fileInputRef.current?.click()}>
                        Start Analysis
                    </button>
                </div>

                <div className="middle-section">
                    <div 
                        className={`upload-card ${isDragging ? 'drag-over' : ''}`}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                    >
                        <div className="avatar">SD</div>
                        
                        <div className="upload-area" onClick={() => !isProcessing && fileInputRef.current?.click()}>
                            <svg className="progress-ring" viewBox="0 0 160 160">
                                <defs>
                                    <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                        <stop offset="0%" stopColor="#7986cb" />
                                        <stop offset="100%" stopColor="#5c6bc0" />
                                    </linearGradient>
                                </defs>
                                <circle
                                    className="progress-bg"
                                    cx="80"
                                    cy="80"
                                    r="72"
                                />
                                <circle
                                    className="progress-bar"
                                    cx="80"
                                    cy="80"
                                    r="72"
                                    strokeDasharray={circumference}
                                    strokeDashoffset={strokeDashoffset}
                                />
                            </svg>
                            <div className="upload-icon-container">
                                <svg className="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                </svg>
                            </div>
                        </div>

                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".pdf"
                            onChange={handleFileChange}
                            className="file-input"
                        />

                        <div className="upload-status">
                            {isProcessing 
                                ? (statusInfo?.status === 'completed' ? 'Analysis Complete!' : 'Analyzing contract...') 
                                : file ? file.name : 'Upload your contract'}
                        </div>
                        <div className="upload-message">
                            {isProcessing 
                                ? `Status: ${statusInfo?.status || 'pending'} - ${progress}%` 
                                : file ? 'Ready to analyze' : 'Click to upload or drag and drop'}
                        </div>

                        <button 
                            className="btn-analyze" 
                            onClick={handleAnalyze}
                            disabled={!file || isProcessing}
                        >
                            Start Analysis
                        </button>
                    </div>
                </div>

                <div className="right-section">
                    {!result ? (
                        <>
                            <h2 className="insights-title">How It Works</h2>
                            <p className="insights-description">
                                Upload your legal contract and our specialized AI agents will analyze it across multiple domains simultaneously.
                            </p>
                            <ul className="feature-list">
                                <li className="feature-item">
                                    <div className="check-icon">
                                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                    </div>
                                    Specialized domain analysis (Compliance, Finance, Legal)
                                </li>
                                <li className="feature-item">
                                    <div className="check-icon">
                                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                    </div>
                                    Identify key clauses and potential risks
                                </li>
                                <li className="feature-item">
                                    <div className="check-icon">
                                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                    </div>
                                    Get professional, actionable recommendations
                                </li>
                            </ul>
                            <button className="btn-download" disabled>
                                Download Report
                            </button>
                        </>
                    ) : (
                        <>
                            <h2 className="insights-title">Analysis Complete!</h2>
                            <div className="pdf-preview">
                                <h3>Contract Analysis Report</h3>
                                {result.contract_type && (
                                    <p><strong>Contract Type:</strong> {result.contract_type}</p>
                                )}
                                {result.industry && (
                                    <p><strong>Industry:</strong> {result.industry}</p>
                                )}
                                <p><strong>Task ID:</strong> {result.task_id}</p>
                                <hr style={{margin: '16px 0', border: 'none', borderTop: '1px solid #e0e0e0'}} />
                                <div style={{whiteSpace: 'pre-wrap', maxHeight: '300px', overflowY: 'auto'}}>
                                    {result.report}
                                </div>
                            </div>
                            <button className="btn-download" onClick={handleDownload}>
                                Download Report
                            </button>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('root'));