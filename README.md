# 🍳 Local Read-Write Agent - Fridge Recipe Assistant

A Langchain-based AI agent that helps you manage your fridge inventory and suggests recipes based on what you have available and your personal preferences. The agent runs locally using Ollama and can read/write to local markdown files to track your fridge contents and preferences.

## Features

- 📋 **Fridge Inventory Management**: Track what's in your fridge with expiration dates
- 🥘 **Recipe Suggestions**: Get personalized recipe recommendations based on available ingredients
- ⚙️ **Preference Management**: Store and update your dietary restrictions, favorite cuisines, and cooking preferences
- 🤖 **Interactive CLI**: Natural language conversation interface
- 🔒 **Local & Private**: Runs entirely on your machine using Ollama (no API keys needed)
- 📝 **Persistent Storage**: Uses markdown files for easy viewing and editing

## Prerequisites

1. **Python 3.11+**: Required for running the application
2. **uv**: Modern Python package manager ([installation guide](https://github.com/astral-sh/uv))
3. **Ollama**: Local LLM runtime ([installation guide](https://ollama.ai))

### Installing Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from https://ollama.ai
```

### Pull the Required Model

```bash
# Pull the model specified in config.yaml (default: gpt-oss:20b)
ollama pull gpt-oss:20b

# Or use another model like llama3.2
ollama pull llama3.2
```

## Installation

1. **Clone or navigate to the project directory**:
```bash
cd local-read-write-agent
```

2. **Install dependencies using uv**:
```bash
uv sync
```

This will create a virtual environment and install all required packages.

## Configuration

The application is configured via `config.yaml`:

```yaml
# Ollama Configuration
ollama:
  model: "gpt-oss:20b"  # Change to your preferred model
  base_url: "http://localhost:11434"
  temperature: 0.7

# Agent Configuration
agent:
  max_iterations: 15
  verbose: true
  early_stopping_method: "generate"

# File Paths
files:
  fridge: "FRIDGE.md"
  preferences: "My-Preference.md"
```

### Available Ollama Models

- `llama3.2` - Fast and efficient
- `llama2` - Reliable general-purpose model
- `mistral` - Good balance of speed and quality
- `gpt-oss:20b` - Larger model for better responses

Change the `model` field in `config.yaml` and pull it with `ollama pull <model-name>`.

## Usage

### Starting the Agent

1. **Make sure Ollama is running**:
```bash
ollama serve
```

2. **Run the agent**:
```bash
uv run python src/main.py
```

### Interactive Commands

- **Ask natural questions**:
  - "What can I cook for dinner tonight?"
  - "Suggest a recipe using chicken and tomatoes"
  - "I just bought eggs and milk, update my fridge"

- **Special commands**:
  - `/help` - Show available commands
  - `/status` - View current fridge and preferences
  - `/exit` or `/quit` - Exit the application

## Project Structure

```
local-read-write-agent/
├── config.yaml              # Configuration file
├── FRIDGE.md               # Fridge inventory (editable)
├── My-Preference.md        # User preferences (editable)
├── pyproject.toml          # Project dependencies
├── src/
│   ├── main.py            # Entry point
│   ├── agent.py           # Agent setup
│   ├── tools/
│   │   └── file_tools.py  # File operation tools
│   └── utils/
│       └── config.py      # Configuration loader
└── README.md
```

## How It Works

1. **File Management Tools**: Uses Langchain's `FileManagementToolkit` for reading/writing markdown files
2. **ReAct Agent**: Implements the ReAct (Reasoning + Acting) pattern for decision-making
3. **Ollama Integration**: Connects to local Ollama instance for LLM inference
4. **Interactive Loop**: Provides a continuous conversation interface with rich formatting

## Customization

### Editing Files Manually

You can directly edit `FRIDGE.md` and `My-Preference.md` with any text editor. The agent will read the updated content on the next query.

### Changing the Model

Edit `config.yaml` and change the `model` field, then pull the new model:

```bash
ollama pull <new-model-name>
```

## Troubleshooting

### "Error initializing Ollama"

- Make sure Ollama is running: `ollama serve`
- Verify the model is installed: `ollama list`
- Check the base_url in config.yaml matches your Ollama instance

### "Import could not be resolved" errors in IDE

These are type-checking warnings and don't affect runtime. The packages are installed in the virtual environment created by uv.

### Agent not finding files

- Ensure `FRIDGE.md` and `My-Preference.md` exist in the project root
- Check file paths in `config.yaml`

## License

MIT License - Feel free to use and modify as needed.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.