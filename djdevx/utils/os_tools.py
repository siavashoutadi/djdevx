import shutil


def is_tool_installed(command: str) -> bool:
    return shutil.which(command) is not None
