"""Agent initialization and setup using simple tool-calling approach."""
from langchain_ollama import OllamaLLM
from langchain_core.tools import BaseTool
from langchain_core.prompts import PromptTemplate
from typing import List, Dict, Any
import sys
import re


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


class SimpleReActAgent:
    """Simple ReAct agent implementation."""
    
    def __init__(self, llm: OllamaLLM, tools: List[BaseTool], max_iterations: int = 15, verbose: bool = True):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.max_iterations = max_iterations
        self.verbose = verbose
        
        # Create tool descriptions
        tool_descriptions = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in tools
        ])
        
        self.prompt_template = PromptTemplate(
            input_variables=["input", "tool_descriptions", "agent_scratchpad"],
            template="""You are a helpful cooking assistant that helps users manage their fridge inventory and suggests recipes based on what they have available and their preferences.

You have access to the following tools:

{tool_descriptions}

Use the following format:

Thought: Think about what you need to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Important guidelines:
- Always read FRIDGE.md to check available ingredients before suggesting recipes
- Always read My-Preference.md to understand dietary restrictions and preferences
- When suggesting recipes, consider expiration dates and use items that will expire soon
- Provide clear, step-by-step cooking instructions
- When updating files with write_file, provide the complete updated content
- Be friendly and helpful in your responses

Begin!

Question: {input}
{agent_scratchpad}"""
        )
        
        self.tool_names = ", ".join(self.tools.keys())
        
    def invoke(self, inputs: Dict[str, str]) -> Dict[str, str]:
        """Run the agent."""
        user_input = inputs.get("input", "")
        agent_scratchpad = ""
        
        for iteration in range(self.max_iterations):
            # Format the prompt
            prompt = self.prompt_template.format(
                input=user_input,
                tool_descriptions="\n".join([f"- {name}: {tool.description}" for name, tool in self.tools.items()]),
                tool_names=self.tool_names,
                agent_scratchpad=agent_scratchpad
            )
            
            if self.verbose:
                print(f"\n--- Iteration {iteration + 1} ---")
            
            # Get LLM response
            response = self.llm.invoke(prompt)
            
            if self.verbose:
                print(f"LLM Response:\n{response}\n")
            
            # Check for Final Answer
            if "Final Answer:" in response:
                final_answer = response.split("Final Answer:")[-1].strip()
                return {"output": final_answer}
            
            # Parse Action and Action Input
            action_match = re.search(r"Action:\s*(.+?)(?:\n|$)", response)
            action_input_match = re.search(r"Action Input:\s*(.+?)(?:\n|$)", response, re.DOTALL)
            
            if action_match and action_input_match:
                action = action_match.group(1).strip()
                action_input = action_input_match.group(1).strip()
                
                # Execute the tool
                if action in self.tools:
                    try:
                        observation = self.tools[action].invoke(action_input)
                        if self.verbose:
                            print(f"Tool: {action}")
                            print(f"Input: {action_input}")
                            print(f"Observation: {observation[:200]}...\n")
                    except Exception as e:
                        observation = f"Error executing tool: {str(e)}"
                        if self.verbose:
                            print(f"Error: {observation}\n")
                else:
                    observation = f"Tool '{action}' not found. Available tools: {self.tool_names}"
                    if self.verbose:
                        print(f"Error: {observation}\n")
                
                # Update scratchpad
                agent_scratchpad += f"\nThought: {response.split('Thought:')[-1].split('Action:')[0].strip()}"
                agent_scratchpad += f"\nAction: {action}"
                agent_scratchpad += f"\nAction Input: {action_input}"
                agent_scratchpad += f"\nObservation: {observation}\n"
            else:
                # If we can't parse, treat the response as the final answer
                return {"output": response}
        
        return {"output": "Maximum iterations reached. Please try rephrasing your question."}


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
    agent = SimpleReActAgent(
        llm=llm,
        tools=tools,
        max_iterations=agent_config.get('max_iterations', 15),
        verbose=agent_config.get('verbose', True)
    )
    
    return agent

# Made with Bob
