# StepSnap Recorder

A local, open-source tool for Windows 11 and Linux to record user steps, capture screenshots, and generate documentation automatically.

## Features
- **Dark Mode GUI**: Sleek, modern interface that stays on top.
- **Multi-Format Export**: Generates JSON, CSV, and a TXT Training Guide.
- **Automatic Screenshots**: Captures a 300x300 thumbnail centered on every mouse click.
- **Global Hotkey**: Press `Ctrl + Alt + S` to stop recording instantly.
- **n8n Ready**: Data is structured for easy import into automation workflows.

## Installation
Ensure you have Python installed, then run:
```bash
pip install pynput pillow
```

## Usage
Run the script:
```bash
python stepsnap.py
```
1. Click **START**.
2. Perform your workflow.
3. Your steps are saved in a unique timestamped folder!
