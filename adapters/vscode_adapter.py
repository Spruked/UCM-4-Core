# UCM_4_Core/adapters/vscode_adapter.py
"""
VS Code Adapter - Desktop-First Capability
Allows ORB to interact with VS Code for coding assistance

ARCHITECTURE:
ORB → VSCodeAdapter → VS Code API/Commands
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import json
import subprocess
import os

logger = logging.getLogger(__name__)

class VSCodeAdapter:
    """
    VS Code integration for ORB desktop capabilities.
    Provides file editing, command execution, and workspace management.
    """

    def __init__(self):
        self.workspace_root = Path.cwd()
        self.vscode_available = self._check_vscode_available()
        self.capabilities = self._get_capabilities()

    def _check_vscode_available(self) -> bool:
        """Check if VS Code is available and accessible"""
        try:
            # Check common VS Code installation paths
            possible_paths = [
                r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd",
                r"C:\Program Files\Microsoft VS Code\bin\code.cmd",
                r"C:\Program Files (x86)\Microsoft VS Code\bin\code.cmd",
                "code"  # In PATH
            ]

            for path in possible_paths:
                try:
                    expanded_path = os.path.expandvars(path)
                    result = subprocess.run(
                        [expanded_path, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        self.vscode_path = expanded_path
                        return True
                except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                    continue

            return False
        except Exception:
            return False

    def _get_capabilities(self) -> Dict[str, bool]:
        """Get available VS Code capabilities"""
        return {
            "file_operations": True,  # Basic file ops always available
            "workspace_commands": self.vscode_available,
            "extension_commands": self.vscode_available,
            "terminal_integration": self.vscode_available,
            "git_operations": self.vscode_available,
            "search_replace": True,  # Can use file system
            "symbol_navigation": self.vscode_available,
        }

    async def execute_command(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """
        Execute a VS Code command via CLI

        Args:
            command: VS Code command (e.g., "workbench.action.quickOpen")
            args: Additional arguments

        Returns:
            Execution result
        """
        if not self.vscode_available:
            return {
                "success": False,
                "error": "VS Code not available",
                "capabilities": self.capabilities
            }

        try:
            cmd_args = ["code"]
            if args:
                cmd_args.extend(args)

            # For commands, we might need different approaches
            # This is a basic implementation - can be extended
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.workspace_root
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def open_file(self, file_path: str, line: int = None, column: int = None) -> Dict[str, Any]:
        """
        Open a file in VS Code

        Args:
            file_path: Path to file (absolute or relative to workspace)
            line: Optional line number
            column: Optional column number
        """
        if not self.vscode_available:
            return {"success": False, "error": "VS Code not available"}

        try:
            abs_path = Path(file_path)
            if not abs_path.is_absolute():
                abs_path = self.workspace_root / file_path

            if not abs_path.exists():
                return {"success": False, "error": f"File not found: {abs_path}"}

            cmd_args = ["code", "--goto", str(abs_path)]
            if line is not None:
                if column is not None:
                    cmd_args[2] = f"{abs_path}:{line}:{column}"
                else:
                    cmd_args[2] = f"{abs_path}:{line}"

            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=10
            )

            return {
                "success": result.returncode == 0,
                "file_path": str(abs_path),
                "line": line,
                "column": column
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def open_folder(self, folder_path: str) -> Dict[str, Any]:
        """
        Open a folder in VS Code

        Args:
            folder_path: Path to folder
        """
        if not self.vscode_available:
            return {"success": False, "error": "VS Code not available"}

        try:
            abs_path = Path(folder_path)
            if not abs_path.is_absolute():
                abs_path = self.workspace_root / folder_path

            if not abs_path.is_dir():
                return {"success": False, "error": f"Folder not found: {abs_path}"}

            result = subprocess.run(
                ["code", str(abs_path)],
                capture_output=True,
                text=True,
                timeout=10
            )

            return {
                "success": result.returncode == 0,
                "folder_path": str(abs_path)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def run_terminal_command(self, command: str, cwd: str = None) -> Dict[str, Any]:
        """
        Run a terminal command in VS Code's integrated terminal

        Args:
            command: Command to run
            cwd: Working directory (defaults to workspace root)
        """
        if not self.capabilities["terminal_integration"]:
            return {"success": False, "error": "Terminal integration not available"}

        # For now, we'll use subprocess directly
        # In a full implementation, this could integrate with VS Code's terminal
        try:
            working_dir = Path(cwd) if cwd else self.workspace_root
            if not working_dir.is_absolute():
                working_dir = self.workspace_root / working_dir

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=working_dir
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": command,
                "cwd": str(working_dir)
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out", "command": command}
        except Exception as e:
            return {"success": False, "error": str(e), "command": command}

    async def search_workspace(self, query: str, include_pattern: str = None) -> Dict[str, Any]:
        """
        Search the workspace using VS Code's search

        Args:
            query: Search query
            include_pattern: File pattern to include (e.g., "*.py")
        """
        if not self.vscode_available:
            return {"success": False, "error": "VS Code not available"}

        try:
            # Use ripgrep or similar for workspace search
            # This is a simplified implementation
            import os
            results = []

            for root, dirs, files in os.walk(self.workspace_root):
                for file in files:
                    if include_pattern:
                        import fnmatch
                        if not fnmatch.fnmatch(file, include_pattern):
                            continue

                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if query.lower() in content.lower():
                                # Find line numbers
                                lines = content.split('\n')
                                matching_lines = []
                                for i, line in enumerate(lines, 1):
                                    if query.lower() in line.lower():
                                        matching_lines.append({
                                            "line": i,
                                            "content": line.strip()
                                        })

                                if matching_lines:
                                    results.append({
                                        "file": str(file_path.relative_to(self.workspace_root)),
                                        "matches": matching_lines
                                    })
                    except:
                        continue

            return {
                "success": True,
                "query": query,
                "results": results,
                "total_files": len(results)
            }

        except Exception as e:
            return {"success": False, "error": str(e), "query": query}

    async def get_workspace_info(self) -> Dict[str, Any]:
        """Get information about the current workspace"""
        try:
            # Count files by extension
            file_counts = {}
            total_files = 0

            for root, dirs, files in os.walk(self.workspace_root):
                for file in files:
                    total_files += 1
                    ext = Path(file).suffix
                    file_counts[ext] = file_counts.get(ext, 0) + 1

            return {
                "success": True,
                "workspace_root": str(self.workspace_root),
                "total_files": total_files,
                "file_types": file_counts,
                "vscode_available": self.vscode_available,
                "capabilities": self.capabilities
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_file(self, file_path: str, content: str = "") -> Dict[str, Any]:
        """
        Create a new file in the workspace

        Args:
            file_path: Path for new file
            content: Initial content
        """
        try:
            abs_path = Path(file_path)
            if not abs_path.is_absolute():
                abs_path = self.workspace_root / file_path

            # Create parent directories if needed
            abs_path.parent.mkdir(parents=True, exist_ok=True)

            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Open in VS Code if available
            if self.vscode_available:
                await self.open_file(str(abs_path))

            return {
                "success": True,
                "file_path": str(abs_path),
                "opened_in_vscode": self.vscode_available
            }

        except Exception as e:
            return {"success": False, "error": str(e), "file_path": file_path}

    async def read_file(self, file_path: str, start_line: int = None, end_line: int = None) -> Dict[str, Any]:
        """
        Read a file from the workspace

        Args:
            file_path: Path to file
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (inclusive)
        """
        try:
            abs_path = Path(file_path)
            if not abs_path.is_absolute():
                abs_path = self.workspace_root / file_path

            if not abs_path.exists():
                return {"success": False, "error": f"File not found: {abs_path}"}

            with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if start_line is not None and end_line is not None:
                # Return specific line range
                start_idx = max(0, start_line - 1)
                end_idx = min(len(lines), end_line)
                content = ''.join(lines[start_idx:end_idx])
                line_count = end_idx - start_idx
            else:
                content = ''.join(lines)
                line_count = len(lines)

            return {
                "success": True,
                "file_path": str(abs_path),
                "content": content,
                "line_count": line_count,
                "total_lines": len(lines)
            }

        except Exception as e:
            return {"success": False, "error": str(e), "file_path": file_path}


# Global adapter instance
_vscode_adapter = None

def get_vscode_adapter() -> VSCodeAdapter:
    """Get or create the VS Code adapter instance"""
    global _vscode_adapter
    if _vscode_adapter is None:
        _vscode_adapter = VSCodeAdapter()
    return _vscode_adapter


# Test the adapter
async def test_vscode_adapter():
    """Test the VS Code adapter functionality"""
    adapter = get_vscode_adapter()

    print("🧪 Testing VS Code Adapter")
    print("=" * 40)

    # Test workspace info
    print("\n1. Workspace Info:")
    info = await adapter.get_workspace_info()
    print(f"   Root: {info.get('workspace_root', 'unknown')}")
    print(f"   VS Code Available: {info.get('vscode_available', False)}")
    print(f"   Total Files: {info.get('total_files', 0)}")

    # Test file operations
    print("\n2. File Operations:")
    test_file = "test_vscode_adapter.txt"
    create_result = await adapter.create_file(test_file, "Hello from VS Code Adapter!")
    print(f"   Created file: {create_result.get('success', False)}")

    if create_result['success']:
        read_result = await adapter.read_file(test_file)
        print(f"   Read file: {read_result.get('success', False)}")
        if read_result['success']:
            print(f"   Content length: {len(read_result.get('content', ''))} chars")

    # Test search
    print("\n3. Workspace Search:")
    search_result = await adapter.search_workspace("def", "*.py")
    print(f"   Search successful: {search_result.get('success', False)}")
    if search_result['success']:
        print(f"   Files found: {search_result.get('total_files', 0)}")

    # Test terminal command
    print("\n4. Terminal Command:")
    cmd_result = await adapter.run_terminal_command("echo 'Hello from VS Code Adapter'")
    print(f"   Command successful: {cmd_result.get('success', False)}")
    if cmd_result['success']:
        print(f"   Output: {cmd_result.get('stdout', '').strip()}")

    print("\n✅ VS Code Adapter test complete!")


if __name__ == "__main__":
    asyncio.run(test_vscode_adapter())