"""File operation tools using Langchain's built-in FileManagementToolkit."""
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_core.tools import BaseTool
from pathlib import Path
from typing import List


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

# Made with Bob
