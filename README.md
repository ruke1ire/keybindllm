# Text Rephrase Service

A systemd service that allows you to instantly rephrase and improve selected text using Ollama and keyboard shortcuts.

## Installation

1. **Install system dependencies:**
   ```bash
   sudo apt install xclip xdotool
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ollama:**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

4. **Start Ollama:**
   ```bash
   ollama serve
   ```

## Quick Usage Guide

1. **Test manually first:**
   ```bash
   DEBUG=1 python3 rephrase.py
   ```

2. **Select text in any application and press Ctrl+Alt+0**

3. **Once working, install as service (see below) to automatically enable the keyboard shortcut.**

## Systemd Installation

```bash
# Install service
mkdir -p ~/.config/systemd/user
cp rephrase.service ~/.config/systemd/user/
# Replace placeholder (__PROJECT_DIR__) with current directory path
sed -i "s|__PROJECT_DIR__|$(pwd)|g" ~/.config/systemd/user/rephrase.service

# Enable and start
systemctl --user daemon-reload
systemctl --user enable rephrase.service
systemctl --user start rephrase.service
```

**Note:** The `rephrase.service` file contains a `__PROJECT_DIR__` placeholder that gets automatically replaced with your current directory path during installation. This allows the service to work regardless of where you clone the repository.

## Uninstall

```bash
# Stop and disable service
systemctl --user stop rephrase.service
systemctl --user disable rephrase.service

# Remove files
rm -f ~/.config/systemd/user/rephrase.service

# Reload systemd
systemctl --user daemon-reload
```

## Environment Variables

Configure these in the service file or export before running manually:

```bash
# Ollama model to use (default: llama3.2)
OLLAMA_MODEL=gemma2

# Keyboard shortcut number (default: 0 for Ctrl+Alt+0)
REPHRASE_KEYNUM=1

# Ollama API URL (default: http://localhost:11434)
OLLAMA_URL=http://localhost:11434
```

## Quick Systemd Debugging

```bash
# Check service status
systemctl --user status rephrase.service

# Stop the service
systemctl --user stop rephrase.service

# Start the service
systemctl --user start rephrase.service

# View logs
systemctl --user logs -f rephrase.service

# Test manually with debug
DEBUG=1 python3 rephrase.py

# Test by selecting text and pressing Ctrl+Alt+0
``` 