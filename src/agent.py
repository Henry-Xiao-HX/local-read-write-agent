"""Simple agent for reading and writing fridge and preference files."""
from langchain_ollama import OllamaLLM
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, AIMessage
from typing import List, Dict, Any
import sys
import yaml
from pathlib import Path
from datetime import datetime


# Configuration functions (integrated from src/utils/config.py)

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration settings
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def get_ollama_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract Ollama configuration.
    
    Args:
        config: Full configuration dictionary
        
    Returns:
        Ollama-specific configuration
    """
    return config.get('ollama', {})


def get_agent_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract agent configuration.
    
    Args:
        config: Full configuration dictionary
        
    Returns:
        Agent-specific configuration
    """
    return config.get('agent', {})


def get_file_paths(config: Dict[str, Any]) -> Dict[str, str]:
    """Extract file paths configuration.
    
    Args:
        config: Full configuration dictionary
        
    Returns:
        File paths dictionary
    """
    return config.get('files', {})


# Tool creation functions (integrated from src/tools/file_tools.py)

def create_file_tools(fridge_path: str, preferences_path: str) -> List[BaseTool]:
    """Create file operation tools using Langchain's FileManagementToolkit.
    
    Args:
        fridge_path: Path to the fridge inventory file
        preferences_path: Path to the preferences file
        
    Returns:
        List of Langchain Tools for file operations
    """
    # Get the working directory (where the files are located)
    working_directory = str(Path.cwd())
    
    # Create the file management toolkit
    # This provides read_file, write_file, list_directory, and other file tools
    toolkit = FileManagementToolkit(
        root_dir=working_directory,
        selected_tools=["read_file", "write_file", "list_directory"]
    )
    
    # Get the tools from the toolkit
    tools = toolkit.get_tools()
    
    return tools


# Agent functions


def initialize_llm(ollama_config: Dict[str, Any]) -> OllamaLLM:
    """Initialize the Ollama LLM.
    
    Args:
        ollama_config: Configuration dictionary for Ollama
        
    Returns:
        Initialized OllamaLLM instance
    """
    try:
        llm = OllamaLLM(
            model=ollama_config.get('model', 'llama3.2'),
            base_url=ollama_config.get('base_url', 'http://localhost:11434'),
            temperature=ollama_config.get('temperature', 0.7),
        )
        return llm
    except Exception as e:
        print(f"Error initializing Ollama: {e}")
        print("\nMake sure Ollama is running. You can start it with: ollama serve")
        print(f"And ensure the model '{ollama_config.get('model')}' is installed.")
        print(f"Install it with: ollama pull {ollama_config.get('model')}")
        sys.exit(1)


class SimpleCookingAgent:
    """Simple cooking assistant agent with session tracking."""
    
    def __init__(self, llm: OllamaLLM, tools: List[BaseTool], verbose: bool = True):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.verbose = verbose
        self.chat_history = []  # Store conversation history as list of messages
        self.session_interactions = []
        
    def invoke(self, inputs: Dict[str, str]) -> Dict[str, str]:
        """Run the agent with automatic file reading."""
        user_input = inputs.get("input", "")
        
        # Automatically read both files to provide context
        fridge_content = ""
        preferences_content = ""
        
        try:
            if "read_file" in self.tools:
                fridge_content = self.tools["read_file"].invoke("FRIDGE.md")
                preferences_content = self.tools["read_file"].invoke("My-Preference.md")
        except Exception as e:
            if self.verbose:
                print(f"Note: Could not read files: {e}")
        
        # Build a comprehensive prompt with context
        prompt = f"""You are a helpful cooking assistant. You help users manage their fridge inventory and suggest recipes.

Current Fridge Inventory:
{fridge_content}

User's Food Preferences:
{preferences_content}

User's Question: {user_input}

Please provide a helpful, friendly response. If the user asks about what's in the fridge, summarize the contents. If they ask for recipe suggestions, consider their preferences and what ingredients are available. If they want to update the fridge, acknowledge what should be changed.

Your response:"""

        if self.verbose:
            print("\n--- Processing Request ---\n")
        
        # Get LLM response
        response = self.llm.invoke(prompt)
        
        if self.verbose:
            print(f"Response generated\n")
        
        # Store interaction in session
        self.session_interactions.append({
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "response": response
        })
        
        # Save to chat history
        self.chat_history.append({"role": "user", "content": user_input})
        self.chat_history.append({"role": "assistant", "content": response})
        
        return {"output": response}
    
    def end_session(self):
        """Analyze session and update preference file if needed."""
        if not self.session_interactions:
            return
        
        try:
            # Step 1: Build session summary from interactions
            session_summary = "\n\n".join([
                f"User: {interaction['user_input']}\nAssistant: {interaction['response']}"
                for interaction in self.session_interactions
            ])
            
            # Step 2: Use LLM to generate a summary including food preferences/allergies
            summary_prompt = f"""Analyze this cooking assistant session and create a concise summary.

Session Conversation:
{session_summary}

Please provide a summary that includes:
1. Main topics discussed
2. Any food preferences mentioned (likes, dislikes, favorite cuisines, etc.)
3. Any dietary restrictions or allergies mentioned
4. Any other relevant information about the user's food habits

If no food preferences or allergies were mentioned, explicitly state "No food preferences or allergies mentioned."

Summary:"""

            session_analysis = self.llm.invoke(summary_prompt)
            
            if self.verbose:
                print(f"\n--- Session Summary ---")
                print(session_analysis)
                print()
            
            # Step 3: Read current preferences and compare with summary
            preferences_content = self.tools["read_file"].invoke("My-Preference.md")
            
            comparison_prompt = f"""Compare the session summary with the current preferences file and determine if updates are needed.

Current Preferences File:
{preferences_content}

Session Summary:
{session_analysis}

Task: Determine if there is any NEW information in the session summary that should be added to the preferences file. Only add information that is NOT already present.

If there is new information to add:
- Provide the COMPLETE updated preferences file content in markdown format
- Integrate the new information into the appropriate existing sections
- Maintain the same structure and formatting as the original file

If there is NO new information to add:
- Respond with exactly: NO_UPDATES_NEEDED

Your response:"""

            comparison_result = self.llm.invoke(comparison_prompt)
            
            # Step 4: Update My-Preference.md if necessary
            if "NO_UPDATES_NEEDED" not in comparison_result:
                # The LLM returned the updated file content directly
                self.tools["write_file"].invoke({
                    "file_path": "My-Preference.md",
                    "text": comparison_result.strip()
                })
                
                if self.verbose:
                    print("✓ Preferences file updated based on session")
            else:
                if self.verbose:
                    print("✓ No preference updates needed")
        
        except Exception as e:
            if self.verbose:
                print(f"\nNote: Could not complete session analysis: {e}")


def create_agent_executor(
    llm: OllamaLLM,
    tools: List[BaseTool],
    agent_config: Dict[str, Any]
):
    """Create the agent executor.
    
    Args:
        llm: The language model
        tools: List of tools available to the agent
        agent_config: Configuration for the agent
        
    Returns:
        Configured agent executor
    """
    agent = SimpleCookingAgent(
        llm=llm,
        tools=tools,
        verbose=agent_config.get('verbose', True)
    )
    
    return agent

# Made with Bob
