# AI Text Services Architecture

This codebase provides a modular framework for creating AI-powered text processing services with global keyboard shortcuts.

## Architecture Overview

### Core Components

```
├── base_service.py       # Base class with keyboard/ollama infrastructure
├── rephrase_service.py   # Rephrase-specific implementation
├── rephrase.py          # Main entry point (backwards compatible)
├── example_service.py   # Example showing how to create new services
└── test_rephrase.py     # Simple test script
```

### Design Pattern

The architecture follows the **Template Method Pattern**:

- **BaseAIService**: Handles common functionality (keyboard shortcuts, ollama communication)
- **Specific Services**: Implement service-specific logic (text handling, prompts, actions)

## Creating New Services

### 1. Inherit from BaseAIService

```python
from base_service import BaseAIService

class YourService(BaseAIService):
    def __init__(self):
        super().__init__("YourServiceName")
        # Your service-specific initialization
```

### 2. Implement Required Methods

```python
def get_system_prompt(self) -> str:
    """Return the AI system prompt for your service"""
    return "Your custom prompt here..."

def process_trigger(self):
    """Main logic when keyboard shortcut is pressed"""
    # 1. Get input (text selection, clipboard, etc.)
    # 2. Process with AI: self.send_to_ollama(prompt, text)
    # 3. Handle output (replace text, save, notify, etc.)
```

### 3. Add Service-Specific Logic

Services can implement different behaviors:

- **Text Sources**: Selected text, clipboard, file, user input
- **AI Processing**: Different prompts and models
- **Output Actions**: Replace text, save to file, show notification, copy to clipboard

## Service Examples

### Rephrase Service (Implemented)
- **Trigger**: Ctrl+Alt+0
- **Input**: Selected text (required)
- **Action**: Grammar correction and improvement
- **Output**: Replace selected text

### Summary Service (Example)
- **Trigger**: Ctrl+Alt+1 
- **Input**: Clipboard text
- **Action**: Text summarization
- **Output**: Log summary

### Future Service Ideas

1. **Translation Service**
   - Input: Selected text
   - Action: Translate to target language
   - Output: Replace text

2. **Code Review Service**
   - Input: Selected code
   - Action: Code analysis and suggestions
   - Output: Show in notification or comments

3. **Email Composer Service**
   - Input: Brief notes
   - Action: Expand into professional email
   - Output: Copy to clipboard

## Base Service Features

### Keyboard Handling
- Configurable shortcuts (Ctrl+Alt+number)
- Environment variable: `REPHRASE_KEYNUM`
- Debug logging for key detection

### Ollama Integration
- Automatic service start/stop
- Model availability checking
- Automatic model downloading
- Robust error handling

### Configuration
- Environment variables for all settings
- Debug logging control
- Flexible model selection

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL` | `gemma3` | AI model to use |
| `REPHRASE_KEYNUM` | `0` | Number key for shortcut |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API URL |
| `DEBUG` | `false` | Enable debug logging |

## Running Services

### Individual Service
```bash
python3 rephrase_service.py      # Rephrase service
python3 example_service.py       # Summary service
```

### Multiple Services (Future)
```bash
# Run multiple services with different shortcuts
REPHRASE_KEYNUM=0 python3 rephrase_service.py &
REPHRASE_KEYNUM=1 python3 example_service.py &
REPHRASE_KEYNUM=2 python3 translate_service.py &
```

### With systemd
Each service can have its own systemd service file with different environment variables.

## Benefits of This Architecture

1. **Reusability**: Common infrastructure shared across services
2. **Maintainability**: Service-specific logic isolated
3. **Extensibility**: Easy to add new services
4. **Consistency**: All services follow same patterns
5. **Testability**: Each component can be tested independently

## Adding New Services - Quick Start

1. Copy `example_service.py` to `your_service.py`
2. Change the class name and service name
3. Update the system prompt for your use case
4. Implement your input/output logic in `process_trigger()`
5. Set a unique `REPHRASE_KEYNUM` environment variable
6. Run and test!

The modular design makes it easy to create specialized AI text services for different workflows while maintaining consistent keyboard shortcuts and AI integration. 