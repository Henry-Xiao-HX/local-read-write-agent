# 🍳 Local Read-Write Agent - Fridge Recipe Assistant

A Langchain-based AI agent that helps you manage your fridge inventory and suggests recipes based on what you have available and your personal preferences. The agent runs locally using Ollama and can read/write to local markdown files to track your fridge contents and preferences.

## Features

- 📋 **Fridge Inventory Management**: Track what's in your fridge with expiration dates
- 🥘 **Recipe Suggestions**: Get personalized recipe recommendations based on available ingredients
- ⚙️ **Preference Management**: Store and update your dietary restrictions, favorite cuisines, and cooking preferences
- 🤖 **Interactive CLI**: Natural language conversation interface
- 🔒 **Local & Private**: Runs entirely on your machine using Ollama (no API keys needed)
- 📝 **Persistent Storage**: Uses markdown files for easy viewing and editing
- 🧠 **Session Tracking**: Automatically updates preferences and fridge inventory based on conversations

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
2. **Session Memory**: Tracks conversations using LangChain's `ConversationBufferMemory`
3. **Ollama Integration**: Connects to local Ollama instance for LLM inference
4. **Interactive Loop**: Provides a continuous conversation interface with rich formatting
5. **Automatic Updates**: Analyzes sessions on exit to update preferences and fridge inventory

## Session Tracking & Auto-Updates

### How Session Tracking Works

The agent now automatically tracks your entire conversation session and intelligently updates your files when you exit.

#### 1. **Automatic Preference Learning**
When you exit (using `/exit` or `/quit`), the agent:
- Analyzes the entire conversation history
- Compares it with your existing `My-Preference.md` file
- Identifies **NEW** preferences, likes, dislikes, or dietary restrictions you mentioned
- Automatically appends new preferences with a timestamp

**Example:**
```
You: I really love spicy Korean food, and I'm trying to avoid processed foods
Assistant: [suggests Korean recipes]
[On exit: Automatically adds "Korean" to favorite cuisines and "avoid processed foods" to health goals]
```

#### 2. **Automatic Fridge Updates After Cooking**
When you exit, the agent also:
- Detects if a recipe was discussed and confirmed to be made
- Identifies which ingredients from your fridge were used
- Automatically updates `FRIDGE.md` by removing or reducing used ingredients
- Updates the "Last updated" timestamp

**Example:**
```
You: What can I make with chicken and tomatoes?
Assistant: [suggests Chicken Tomato Pasta]
You: Perfect! I'll make that tonight.
[On exit: Automatically removes chicken and tomatoes from fridge inventory]
```

#### 3. **Smart Detection**
- **No Duplicates**: Only adds NEW information not already in your preferences
- **Context-Aware**: Understands the full conversation context
- **Confirmation Required**: Only updates fridge when you clearly confirm making a recipe
- **Safe Updates**: All changes are additive and timestamped

### Session Exit Behavior

When you type `/exit` or `/quit`:
1. Agent displays: "Analyzing session and updating files..."
2. Analyzes conversation for new preferences
3. Checks if any recipes were made
4. Updates files automatically
5. Displays confirmation messages

Even if you interrupt with Ctrl+C, the session is saved and analyzed.

### Benefits

- **Effortless Tracking**: No manual file editing needed
- **Natural Interaction**: Just talk naturally about food and cooking
- **Always Up-to-Date**: Your preferences and fridge stay current automatically
- **Full History**: All updates include timestamps for tracking changes

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