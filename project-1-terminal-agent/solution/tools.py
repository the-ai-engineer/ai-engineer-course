"""
Terminal Agent Tools - Solution

Complete implementation of all tools for the terminal agent.
"""

import os
import subprocess
from datetime import datetime

# =============================================================================
# Tool Implementations
# =============================================================================


def list_directory(path: str = ".") -> str:
    """List files and directories at the given path."""
    try:
        entries = os.scandir(path)
        items = []
        for entry in entries:
            type_indicator = "/" if entry.is_dir() else ""
            items.append(f"{entry.name}{type_indicator}")

        if not items:
            return f"Directory '{path}' is empty."

        return "\n".join(sorted(items))

    except FileNotFoundError:
        return f"Error: Directory '{path}' not found."
    except PermissionError:
        return f"Error: Permission denied accessing '{path}'."
    except Exception as e:
        return f"Error listing directory: {e}"


def read_file(path: str, max_lines: int | None = None) -> str:
    """Read contents of a file, optionally limiting to first N lines."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            if max_lines:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line)
                content = "".join(lines)
                if i >= max_lines:
                    content += f"\n... (truncated after {max_lines} lines)"
            else:
                content = f.read()

        # Limit very long files
        if len(content) > 10000:
            content = content[:10000] + "\n... (truncated, file too long)"

        return content

    except FileNotFoundError:
        return f"Error: File '{path}' not found."
    except PermissionError:
        return f"Error: Permission denied reading '{path}'."
    except UnicodeDecodeError:
        return f"Error: '{path}' appears to be a binary file."
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(path: str, content: str) -> str:
    """Write content to a file, creating or overwriting."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{path}'."

    except PermissionError:
        return f"Error: Permission denied writing to '{path}'."
    except Exception as e:
        return f"Error writing file: {e}"


def run_command(command: str) -> str:
    """Execute a shell command and return the output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            if output:
                output += "\n"
            output += f"[stderr] {result.stderr}"

        if not output:
            output = "(no output)"

        if result.returncode != 0:
            output += f"\n[exit code: {result.returncode}]"

        # Limit very long output
        if len(output) > 5000:
            output = output[:5000] + "\n... (truncated)"

        return output

    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error running command: {e}"


def get_file_info(path: str) -> str:
    """Get metadata about a file (size, modified date, type)."""
    try:
        stat = os.stat(path)

        # Human-readable size
        size = stat.st_size
        if size < 1024:
            size_str = f"{size} bytes"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"

        # Formatted modification time
        mtime = datetime.fromtimestamp(stat.st_mtime)
        mtime_str = mtime.strftime("%Y-%m-%d %H:%M:%S")

        # File type
        if os.path.isdir(path):
            type_str = "directory"
        elif os.path.islink(path):
            type_str = "symbolic link"
        else:
            type_str = "file"

        return (
            f"Path: {path}\nType: {type_str}\nSize: {size_str}\nModified: {mtime_str}"
        )

    except FileNotFoundError:
        return f"Error: '{path}' not found."
    except PermissionError:
        return f"Error: Permission denied accessing '{path}'."
    except Exception as e:
        return f"Error getting file info: {e}"


# =============================================================================
# Tool Registry
# =============================================================================

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

TOOLS = [
    {
        "type": "function",
        "name": "list_directory",
        "description": "List files and directories at a given path. Returns a list of filenames, with directories marked with a trailing slash.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to list. Defaults to current directory.",
                }
            },
            "required": [],
        },
    },
    {
        "type": "function",
        "name": "read_file",
        "description": "Read the contents of a file. Can optionally limit to first N lines for large files.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read.",
                },
                "max_lines": {
                    "type": "integer",
                    "description": "Maximum number of lines to read. If not specified, reads the entire file.",
                },
            },
            "required": ["path"],
        },
    },
    {
        "type": "function",
        "name": "write_file",
        "description": "Write content to a file, creating it if it doesn't exist or overwriting if it does.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write.",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file.",
                },
            },
            "required": ["path", "content"],
        },
    },
    {
        "type": "function",
        "name": "run_command",
        "description": "Execute a shell command and return the output. Use for running git, grep, find, or other CLI tools. Has a 30-second timeout.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute.",
                }
            },
            "required": ["command"],
        },
    },
    {
        "type": "function",
        "name": "get_file_info",
        "description": "Get metadata about a file including its size, modification date, and type.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to get info about.",
                }
            },
            "required": ["path"],
        },
    },
]
