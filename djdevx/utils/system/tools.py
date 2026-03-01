import shutil


class SystemTools:
    """Utilities for interacting with the operating system."""

    @staticmethod
    def is_tool_installed(command: str) -> bool:
        """Check if a CLI tool is available on PATH."""
        return shutil.which(command) is not None


system_tools = SystemTools()
