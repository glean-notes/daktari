from typing import Optional


def get_tool_version_from_string(tool: str, file_content: str) -> Optional[str]:
    lines = file_content.split("\n")
    for line in lines:
        clean_line = line.split("#")[0].strip()
        if clean_line.startswith(tool + " "):
            return clean_line.split()[1]
    return None


def get_tool_version(tool: str) -> Optional[str]:
    with open(".tool-versions", "r") as f:
        file_content = f.read()
    return get_tool_version_from_string(tool, file_content)
