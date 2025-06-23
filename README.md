# Text Rephrase Service

A systemd service that allows you to instantly rephrase and improve selected text using Ollama and keyboard shortcuts.

## Features

- Global keyboard shortcut (Ctrl+Alt+0 by default)
- Automatically corrects grammar and improves writing while preserving tone
- Works with any application that supports text selection
- Runs as a systemd user service
- **Modular architecture** - easily extensible for creating new AI text services

## Prerequisites

### System packages
```bash
sudo apt install xclip xdotool
```

### Python packages
```bash
pip install -r requirements.txt
```

### Ollama
Make sure Ollama is installed and has a language model available (default: gemma3).

## Setup

1. **Install system dependencies:**
   ```bash
   sudo apt install xclip xdotool
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure Ollama is running:**
   ```bash
   # Start Ollama service
   ollama serve
   
   # The script will automatically pull the model if it's not available,
   # but you can also pull it manually:
   ollama pull gemma3
   ```

4. **Test the script manually first:**
   ```bash
   # Run with debug output to verify everything works
   DEBUG=1 python3 rephrase.py
   
   # Or use the simple test script
   python3 test_rephrase.py
   ```

5. **Install as systemd service** (see Systemd Installation section below)

## Usage

### Manual Mode (for testing)
```bash
# Run with debug output to see detailed logs
DEBUG=1 python3 rephrase.py

# Exit with Escape key
```

### Test Script (recommended for initial testing)
```bash
# 1. Select text in any application
# 2. Run the test script
python3 test_rephrase.py

# This will show you the original vs rephrased text and ask before replacing
```

### Service Mode (automated)
1. Select any text in any application
2. Press **Ctrl+Alt+0** (or your configured key)
3. The selected text will be automatically replaced with the improved version

### Example
- **Original**: "this are a example text with grammer mistakes"
- **After Ctrl+Alt+0**: "This is an example text with grammar corrections"

## Configuration

Set these environment variables in the service file:

- `OLLAMA_MODEL`: Ollama model to use (default: llama3.2)
- `REPHRASE_KEYNUM`: Number key for the shortcut (default: 0 for Ctrl+Alt+0)
- `OLLAMA_URL`: Ollama API URL (default: http://localhost:11434)

## Systemd Installation

To install and run as a system service:

1. **Install the service:**
   ```bash
   # Copy service file to systemd user directory
   mkdir -p ~/.config/systemd/user
   cp rephrase.service ~/.config/systemd/user/
   
   # Update the ExecStart path to match your installation
   sed -i "s|%h/Projects/keybindllm|$(pwd)|g" ~/.config/systemd/user/rephrase.service
   ```

2. **Enable and start the service:**
   ```bash
   systemctl --user daemon-reload
   systemctl --user enable rephrase.service
   systemctl --user start rephrase.service
   ```

3. **Check service status:**
   ```bash
   systemctl --user status rephrase.service
   ```

4. **View service logs:**
   ```bash
   systemctl --user logs -f rephrase.service
   ```

5. **Stop the service:**
   ```bash
   systemctl --user stop rephrase.service
   ```

## Debugging

### Manual Testing (Recommended)

For detailed debugging, run the script manually with debug logging:

```bash
# Run with detailed debug output
DEBUG=1 python3 rephrase.py
```

This will show:
- ✅ Detailed key press detection
- 📝 Original text vs rephrased text comparison
- 🔄 Step-by-step text replacement process
- 🤖 Ollama communication details

### Quick Testing Without Shortcuts

Use the test script to verify core functionality:

```bash
# 1. Select some text in any application
# 2. Run the test script:
python3 test_rephrase.py
```

This bypasses keyboard shortcuts and tests:
- Text selection detection
- Ollama communication
- Text replacement logic

### Service Debugging

To debug the systemd service:

```bash
# Check service status
systemctl --user status rephrase.service

# View real-time logs
systemctl --user logs -f rephrase.service

# Restart service with debug logging
systemctl --user edit rephrase.service
# Add: Environment=DEBUG=1

systemctl --user daemon-reload
systemctl --user restart rephrase.service
```

## Troubleshooting

- **Service not starting**: 
  - Check logs with `systemctl --user status rephrase.service`
  - Verify the ExecStart path in the service file is correct
  - Ensure Python dependencies are installed

- **Keyboard shortcut not working**: 
  - Run with `DEBUG=1` to see key detection
  - Ensure the service is running and check X11 permissions
  - Try different modifier keys (some systems vary)

- **Text not being replaced**: 
  - Verify `xdotool` and `xclip` are installed: `sudo apt install xclip xdotool`
  - Check if text is properly selected (try the test script first)
  - Ensure the target application accepts Ctrl+V for pasting

- **Ollama connection issues**: 
  - Make sure Ollama is running: `ollama serve`
  - Check if the model is available: `ollama list`
  - The script automatically pulls missing models, but you can do it manually: `ollama pull gemma3`
  - Test the model manually: `ollama run gemma3` (then type a test message)
  - Verify Ollama URL in configuration

- **Permission issues**:
  - Some systems require running with elevated permissions for global key detection
  - Try running manually first to isolate permission issues

## Extending the Framework

This codebase now uses a **modular architecture** that separates general keyboard/AI infrastructure from service-specific logic. 

### Architecture
- **`base_service.py`**: Reusable keyboard shortcuts and Ollama integration
- **`rephrase_service.py`**: Rephrase-specific text handling
- **`rephrase.py`**: Backwards-compatible entry point

### Creating New Services

To create a new AI text service (translation, summarization, etc.):

1. Copy `example_service.py` as a template
2. Inherit from `BaseAIService`
3. Implement your specific prompt and text processing logic
4. Set a unique keyboard shortcut number

See `ARCHITECTURE.md` for detailed documentation and examples.

### Future Service Ideas
- **Translation**: Ctrl+Alt+1 to translate selected text
- **Summarization**: Ctrl+Alt+2 to summarize clipboard content  
- **Code Review**: Ctrl+Alt+3 to analyze selected code
- **Email Composer**: Ctrl+Alt+4 to expand notes into emails 