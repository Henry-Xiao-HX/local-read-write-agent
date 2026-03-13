"""Configuration loader for the agent."""
import yaml
from pathlib import Path
from typing import Dict, Any


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

# Made with Bob
