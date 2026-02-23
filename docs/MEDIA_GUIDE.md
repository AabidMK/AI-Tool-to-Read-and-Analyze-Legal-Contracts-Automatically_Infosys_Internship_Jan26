# 📸 How to Add Screenshots and Video

## Step 1: Capture Screenshots

### On macOS:
1. Press `Cmd + Shift + 4` to take a screenshot
2. Drag to select the area
3. Screenshot saves to Desktop

### On Windows:
1. Press `Windows + Shift + S`
2. Select area
3. Save from clipboard

### What to Capture:
1. **upload.png** - The initial upload page with drag-drop zone
2. **processing.png** - Pipeline showing active processing steps
3. **results.png** - Full results page with summary and analyses
4. **analysis-detail.png** - Drawer open showing detailed findings

## Step 2: Record Demo Video

### Option A: Screen Recording (Recommended)
**macOS:**
```bash
# Press Cmd + Shift + 5, select record
# Or use QuickTime Player > File > New Screen Recording
```

**Windows:**
```bash
# Press Windows + G (Game Bar)
# Click record button
```

### Option B: Convert to GIF (Better for GitHub)
1. Record video (keep under 30 seconds)
2. Go to https://ezgif.com/video-to-gif
3. Upload your video
4. Resize to 800px width
5. Download GIF (keep under 10MB)

## Step 3: Add Files to Repo

```bash
# Navigate to project root
cd /Users/lakshanagopu/Desktop/AI/AI-Tool-to-Read-and-Analyze-Legal-Contracts-Automatically_Infosys_Internship_Jan26

# Copy your screenshots
cp ~/Desktop/upload.png docs/images/
cp ~/Desktop/processing.png docs/images/
cp ~/Desktop/results.png docs/images/
cp ~/Desktop/analysis-detail.png docs/images/

# Copy your video/gif
cp ~/Desktop/demo.gif docs/videos/

# Add to git
git add docs/
git commit -m "docs: Add screenshots and demo video"
git push origin lakshana_g
```

## Step 4: Verify on GitHub

1. Go to your repo on GitHub
2. Navigate to README.md
3. Screenshots and video should display automatically

## Tips:
- Keep images under 1MB each (compress if needed)
- GIF should be under 10MB for GitHub
- Use 16:9 aspect ratio for video
- Show complete workflow: Upload → Process → Results → Detail
- Make sure UI is clean (no personal info visible)

## Alternative: Use GitHub Issues for Hosting
If files are too large:
1. Create a GitHub issue in your repo
2. Drag-drop images into the issue comment
3. Copy the generated URLs
4. Update README.md with those URLs
5. Close the issue
