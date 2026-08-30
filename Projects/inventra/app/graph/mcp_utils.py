import json
from typing import Any


def normalize_mcp_output(result: Any) -> Any:
    """Convert MCP content wrappers into normal Python data."""

    if result is None:
        return None

    if isinstance(result, list):
        if not result:
            return {}
        if len(result) == 1:
            return normalize_mcp_output(result[0])
        return [normalize_mcp_output(item) for item in result]

    if isinstance(result, dict):
        # FastMCP text block:
        # {"type": "text", "text": "{\"key\":\"value\"}", ...}
        if result.get("type") == "text" and "text" in result:
            return normalize_mcp_output(result["text"])
        return result

    if isinstance(result, str):
        try:
            return normalize_mcp_output(json.loads(result))
        except json.JSONDecodeError:
            return {"text": result}

    artifact = getattr(result, "artifact", None)
    if artifact is not None:
        return normalize_mcp_output(artifact)

    text = getattr(result, "text", None)
    if text is not None:
        return normalize_mcp_output(text)

    content = getattr(result, "content", None)
    if content is not None:
        return normalize_mcp_output(content)

    return result


def get_error(result: Any) -> str | None:
    if isinstance(result, dict) and result.get("error"):
        return str(result["error"])
    return None
