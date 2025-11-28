"""
Terminal Agent Tools

Implement the tool functions and schemas for the terminal agent.

Each tool should:
- Take typed arguments
- Return a string result
- Handle errors gracefully (return error message, don't raise)
"""

import os
import subprocess

# =============================================================================
# Tool Implementations
# =============================================================================


def list_directory(path: str = ".") -> str:
    """List files and directories at the given path."""
    # TODO: Implement this
    # - Use os.listdir() or os.scandir()
    # - Handle FileNotFoundError, PermissionError
    # - Return a formatted string of results
    pass


def read_file(path: str, max_lines: int | None = None) -> str:
    """Read contents of a file, optionally limiting to first N lines."""
    # TODO: Implement this
    # - Handle FileNotFoundError, PermissionError
    # - If max_lines is set, only return that many lines
    # - Be careful with binary files
    pass


def write_file(path: str, content: str) -> str:
    """Write content to a file, creating or overwriting."""
    # TODO: Implement this
    # - Handle PermissionError
    # - Return confirmation message
    pass


def run_command(command: str) -> str:
    """Execute a shell command and return the output."""
    # TODO: Implement this
    # - Use subprocess.run()
    # - Set a timeout (e.g., 30 seconds)
    # - Capture both stdout and stderr
    # - Handle errors gracefully
    #
    # SAFETY NOTE: In production, you'd want to:
    # - Whitelist allowed commands
    # - Run in a sandbox
    # - Limit resource usage
    pass


def get_file_info(path: str) -> str:
    """Get metadata about a file (size, modified date, type)."""
    # TODO: Implement this
    # - Use os.stat()
    # - Return human-readable size
    # - Return formatted modification time
    pass


# =============================================================================
# Tool Registry
# =============================================================================

# Maps tool names to functions
TOOL_REGISTRY = {
    "list_directory": list_directory,
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command,
    "get_file_info": get_file_info,
}


# =============================================================================
# Tool Schemas
# =============================================================================

# Define the JSON schemas for each tool
# The LLM uses these to understand what tools are available

TOOLS = [
    # TODO: Define schema for list_directory
    # {
    #     "type": "function",
    #     "name": "list_directory",
    #     "description": "...",
    #     "parameters": { ... }
    # },
    # TODO: Define schema for read_file
    # TODO: Define schema for write_file
    # TODO: Define schema for run_command
    # TODO: Define schema for get_file_info
]
