"""Main entry point for the local read-write agent."""
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import load_config, get_ollama_config, get_agent_config, get_file_paths
from tools.file_tools import create_file_tools
from agent import initialize_llm, create_agent_executor


console = Console()


def print_welcome():
    """Print welcome message."""
    welcome_text = """
# 🍳 Fridge Recipe Assistant

Welcome! I'm your personal cooking assistant. I can help you:
- 📋 Check what's in your fridge
- 🥘 Suggest recipes based on available ingredients
- 📝 Update your fridge inventory
- ⚙️  Manage your food preferences

**Commands:**
- Type your questions naturally (e.g., "What can I cook for dinner?")
- `/help` - Show available commands
- `/status` - View current fridge and preferences
- `/exit` or `/quit` - Exit the application

Let's get cooking! 👨‍🍳
    """
    console.print(Panel(Markdown(welcome_text), border_style="green"))


def print_help():
    """Print help information."""
    help_text = """
# Available Commands

- **Natural questions**: Ask anything about recipes, ingredients, or cooking
  - "What can I make with chicken and tomatoes?"
  - "Suggest a quick dinner recipe"
  - "I just bought eggs and milk, update my fridge"
  
- **/help**: Show this help message
- **/status**: Display current fridge inventory and preferences
- **/exit** or **/quit**: Exit the application

# Tips
- The agent will automatically read your fridge and preferences when needed
- Be specific about quantities when updating your fridge
- Mention dietary restrictions or preferences in your questions
    """
    console.print(Panel(Markdown(help_text), border_style="blue"))


def print_status(fridge_path: str, preferences_path: str):
    """Print current status of fridge and preferences."""
    try:
        with open(fridge_path, 'r') as f:
            fridge_content = f.read()
        
        with open(preferences_path, 'r') as f:
            preferences_content = f.read()
        
        console.print("\n[bold cyan]📋 Current Fridge Inventory:[/bold cyan]")
        console.print(Panel(Markdown(fridge_content), border_style="cyan"))
        
        console.print("\n[bold magenta]⚙️  Your Preferences:[/bold magenta]")
        console.print(Panel(Markdown(preferences_content), border_style="magenta"))
    except Exception as e:
        console.print(f"[red]Error reading files: {e}[/red]")


def main():
    """Main function to run the interactive agent."""
    agent_executor = None  # Initialize to None for error handling
    
    try:
        # Load configuration
        config = load_config()
        ollama_config = get_ollama_config(config)
        agent_config = get_agent_config(config)
        file_paths = get_file_paths(config)
        
        # Print welcome message
        print_welcome()
        
        # Initialize LLM
        console.print("[yellow]Initializing Ollama LLM...[/yellow]")
        llm = initialize_llm(ollama_config)
        console.print("[green]✓ LLM initialized successfully![/green]\n")
        
        # Create tools
        tools = create_file_tools(
            file_paths.get('fridge', 'FRIDGE.md'),
            file_paths.get('preferences', 'My-Preference.md')
        )
        
        # Create agent executor
        agent_executor = create_agent_executor(llm, tools, agent_config)
        
        # Interactive loop
        console.print("[bold green]Agent ready! Start asking questions...[/bold green]\n")
        
        while True:
            try:
                # Get user input
                user_input = console.input("[bold blue]You:[/bold blue] ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['/exit', '/quit']:
                    console.print("\n[yellow]Analyzing session and updating files...[/yellow]")
                    agent_executor.end_session()
                    console.print("[yellow]Thanks for using Fridge Recipe Assistant! Goodbye! 👋[/yellow]")
                    break
                
                if user_input.lower() == '/help':
                    print_help()
                    continue
                
                if user_input.lower() == '/status':
                    print_status(
                        file_paths.get('fridge', 'FRIDGE.md'),
                        file_paths.get('preferences', 'My-Preference.md')
                    )
                    continue
                
                # Process with agent
                console.print("\n[yellow]🤔 Thinking...[/yellow]\n")
                
                # Langchain agents use 'input' key
                response = agent_executor.invoke({"input": user_input})
                
                # Extract output from response
                output = response.get('output', 'No response generated.')
                
                # Print response
                console.print("\n[bold green]Assistant:[/bold green]")
                console.print(Panel(
                    Markdown(output),
                    border_style="green"
                ))
                console.print()
                
            except KeyboardInterrupt:
                console.print("\n\n[yellow]Interrupted. Analyzing session and updating files...[/yellow]")
                agent_executor.end_session()
                console.print("[yellow]Session saved. Type /exit to quit or continue asking questions.[/yellow]\n")
                continue
            except Exception as e:
                console.print(f"\n[red]Error processing request: {e}[/red]\n")
                if agent_config.get('verbose'):
                    import traceback
                    console.print(f"[red]{traceback.format_exc()}[/red]")
                continue
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Exiting... Analyzing session and updating files...[/yellow]")
        if agent_executor is not None:
            try:
                agent_executor.end_session()
            except:
                pass
        console.print("[yellow]Goodbye! 👋[/yellow]")
        sys.exit(0)
    except FileNotFoundError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        console.print("[yellow]Make sure config.yaml exists in the project root.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        import traceback
        console.print(f"[red]{traceback.format_exc()}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
