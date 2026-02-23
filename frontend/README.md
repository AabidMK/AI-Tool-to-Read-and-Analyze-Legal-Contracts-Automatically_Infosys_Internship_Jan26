# LexAI Frontend

Modern web interface for the Contract Classifier API.

## Features

- PDF contract upload (drag & drop or click)
- Real-time processing pipeline visualization
- Contract classification and expert analysis display
- Markdown report download
- Clean, minimal UI with dark theme

## Setup

1. **Start the backend API first:**
   ```bash
   cd ../contract-classifier
   python api.py
   ```

2. **Serve the frontend:**
   
   Using Python:
   ```bash
   python -m http.server 3000
   ```
   
   Or using Node.js:
   ```bash
   npx serve -p 3000
   ```

3. **Open in browser:**
   ```
   http://localhost:3000
   ```

## Configuration

The API endpoint is configured in `app.js`:
```javascript
const API_BASE = 'http://localhost:8000';
```

Change this if your backend runs on a different port.

## Usage

1. Click "Upload PDF" or drag & drop a contract PDF
2. Watch the processing pipeline progress
3. View contract summary and expert analyses
4. Click on any analysis to see detailed findings
5. Download the full markdown report

## Files

- `index.html` - Main HTML structure
- `styles.css` - All styling (dark theme, animations)
- `app.js` - API integration and UI logic

## API Endpoints Used

- `POST /analyze` - Upload and analyze contract
- `GET /result/{task_id}` - Poll for results
- `GET /download/{task_id}` - Download markdown report
- `GET /health` - Check API status
