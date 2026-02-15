"""Natural language command parser for Solid CLI."""

import re
from typing import Union, Tuple


def parse_natural_language(prompt: str) -> Union[Tuple[str, str, str], str]:
    """Parse natural language commands into CLI intents.
    
    Supports:
    - "Upload [file] to [remote]" -> ("sync", file, remote)
    - "Share [file] with [user]" -> ("share", file, user)
    - "List files in [remote]" -> ("ls", remote)
    
    Args:
        prompt: Natural language command string
    
    Returns:
        Tuple of (intent, arg1, arg2) or error message string
    """
    prompt = prompt.strip()
    
    # Pattern 1: Upload [file] to [remote]
    upload_match = re.search(
        r"^(?:upload|sync)\s+([^\s]+)\s+to\s+([^\s]+)$",
        prompt,
        re.IGNORECASE
    )
    if upload_match:
        file_path = upload_match.group(1)
        remote_url = upload_match.group(2)
        return ("sync", file_path, remote_url)
    
    # Pattern 2: Share [file] with [user]
    share_match = re.search(
        r"^share\s+([^\s]+)\s+with\s+([^\s]+)$",
        prompt,
        re.IGNORECASE
    )
    if share_match:
        file_path = share_match.group(1)
        user_webid = share_match.group(2)
        return ("share", file_path, user_webid)
    
    # Pattern 3: List files in [remote]
    list_match = re.search(
        r"^(?:list|ls)\s+(?:files\s+)?in\s+([^\s]+)$",
        prompt,
        re.IGNORECASE
    )
    if list_match:
        remote_url = list_match.group(1)
        return ("ls", remote_url, "")
    
    # No match found
    return "I'm sorry, I didn't understand that command."
