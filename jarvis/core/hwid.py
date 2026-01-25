from __future__ import annotations

import subprocess
import uuid


def get_hwid() -> str:
    """Return a stable Windows HWID using WMIC, fallback to UUID."""
    try:
        output = subprocess.check_output(
            ["wmic", "csproduct", "get", "uuid"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        if len(lines) >= 2:
            return lines[1]
    except Exception:
        pass

    node = uuid.getnode()
    return f"NODE-{node}"
