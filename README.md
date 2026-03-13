# Local Read-Write Agent: LLM-Powered Fridge Assistant 🍳

A fun weekend project that turned into a surprisingly useful AI agent for managing your fridge and getting recipe suggestions. Built with local LLMs because who wants to pay API fees for asking "what's for dinner?"

## Architecture (The Fun Stuff)

### How It Actually Works

**Agent Design**: I built a simple ReAct-style agent that reads your fridge contents, remembers your preferences, and suggests recipes. No fancy frameworks—just a straightforward agent loop that talks to Ollama and manipulates markdown files.

**Inference Pipeline**:
- **Model**: Whatever Ollama model you want (I like llama3.2 for speed)
- **Context Injection**: Automatically reads your fridge and preferences before every query
- **Tool System**: LangChain's FileManagementToolkit for reading/writing markdown
- **Memory**: Keeps conversation history in memory, analyzes it on exit

**Data Flow**:
```
You ask a question → Agent reads FRIDGE.md + My-Preference.md → 
LLM thinks about it → Gives you an answer → 
(Optional) Updates files if needed
```

### Core Components

**SimpleCookingAgent** (`src/agent.py`):
- Custom agent class that's way simpler than using LangChain's built-in agents
- Automatically loads your fridge/preferences into every prompt
- Tracks your entire conversation session
- On exit, uses the LLM to analyze what you talked about and updates your preferences

**Inference Config** (`config.yaml`):
- Temperature: 0.7 (sweet spot for creative but coherent recipes)
- Max iterations: 15 (prevents the agent from going crazy)
- Verbose mode so you can see what's happening

**Tool System**:
- `read_file`: Grabs markdown files
- `write_file`: Saves updates
- `list_directory`: Looks around (rarely used)

## Technical Highlights

### 1. Smart Session Tracking
When you exit, the agent does something clever:
- Reads your entire conversation
- Asks the LLM: "Did the user mention any new preferences?"
- Compares with existing preferences
- Only updates if there's actually new info
- Timestamps everything

### 2. Context-Aware Prompting
Every query automatically includes:
- Current fridge inventory
- Your food preferences
- The actual question you asked

This means the LLM always has full context without you repeating yourself.

### 3. Two Modes of Operation
- **Interactive**: Chat back and forth, perfect for exploring recipe ideas
- **Single-shot**: One question, one answer, done. Great for scripts or quick queries.

### 4. Markdown-Based State
Why markdown? Because:
- You can edit it manually with any text editor
- Git-friendly (track your fridge history!)
- Human-readable
- No database setup required

## Prerequisites

- **Python 3.11+**: Modern Python features
- **uv**: Fast package manager (way better than pip)
- **Ollama**: Run LLMs locally (free, private, fast)

## Quick Start

```bash
# Install everything
uv sync

# Get a model (llama3.2 is fast and good)
ollama pull llama3.2

# Start chatting
uv run python src/main.py
```

## Configuration

Edit `config.yaml` to tune the agent:

```yaml
ollama:
  model: "llama3.2"           # Try mistral or gpt-oss:20b too
  temperature: 0.7            # Higher = more creative recipes

agent:
  max_iterations: 15          # Safety limit
  verbose: true               # See what's happening
```

## Usage Examples

### Interactive Mode
```bash
uv run python src/main.py

# Then chat naturally:
# "What can I make with chicken and tomatoes?"
# "I just bought eggs and milk"
# "Suggest something spicy"
```

### Single-Shot Mode (for scripting)
```bash
uv run python src/main.py -p "What's in my fridge?"
uv run python src/main.py -p "Quick dinner idea?"
```

### Commands
- `/status`: See your current fridge and preferences
- `/help`: Show available commands
- `/exit`: Analyze session and save updates

## Implementation Deep Dive

### The Inference Strategy

**Prompt Engineering**:
I use a simple but effective prompt structure:
1. System role: "You are a helpful cooking assistant"
2. Context injection: Current fridge + preferences
3. User question
4. Clear instructions on what to do

**Session Analysis Magic**:
When you exit, the agent runs a 3-step pipeline:
1. **Summarize**: "What did we talk about?"
2. **Compare**: "Is any of this new information?"
3. **Update**: "Write the updated preferences file"

This means you can casually mention "I love Thai food" and it'll remember next time.

### Why This Architecture?

**Simplicity over complexity**: I could've used LangChain's full agent framework, but honestly, a simple loop with direct LLM calls is easier to understand and debug.

**Local-first**: Everything runs on your machine. No API keys, no usage limits, no privacy concerns.

**File-based state**: Markdown files are the perfect database for this use case. Easy to inspect, easy to edit, easy to version control.

### Performance Notes

- **Speed**: 2-5 seconds per response (depends on your model)
- **Context**: Limited by model's context window (usually 4K-8K tokens)
- **Memory**: Conversation history grows with session length
- **Disk**: Minimal I/O, only writes on updates

## Project Structure

```
local-read-write-agent/
├── config.yaml              # Tweak inference settings here
├── FRIDGE.md               # Your inventory (edit manually if you want)
├── My-Preference.md        # Your preferences (auto-updated)
├── src/
│   ├── agent.py           # The brain of the operation
│   └── main.py            # CLI interface
└── pyproject.toml         # Dependencies
```

## Troubleshooting

**"Error initializing Ollama"**:
```bash
ollama serve  # Make sure Ollama is running
ollama list   # Check if your model is installed
```

**Slow responses**:
- Try a smaller model (llama3.2 is fast)
- Use quantized versions (Q4, Q5)
- Lower the temperature

**Agent seems confused**:
- Check your markdown files aren't corrupted
- Try `/status` to see what it's reading
- Enable verbose mode in config.yaml

## Future Ideas

- [ ] Add recipe database integration
- [ ] Implement ingredient expiration warnings
- [ ] Support for meal planning
- [ ] Shopping list generation
- [ ] Multi-user support (roommates!)

## License

MIT - Do whatever you want with it!

## Credits

Built as a personal project to learn about:
- Local LLM agents
- File-based state management
- Prompt engineering for context injection
- Session-based preference learning

Turns out it's actually pretty useful for real cooking decisions. Who knew? 🤷‍♂️