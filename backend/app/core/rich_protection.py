"""
Rich library protection module to prevent recursion errors.
This module provides utilities to safely handle Rich library operations
and prevent recursion issues when logging complex objects.
"""

import os
import sys
from typing import Any, Dict, Optional


def disable_rich_completely():
    """Completely disable Rich library to prevent recursion issues."""
    # Set environment variable to disable Rich
    os.environ["RICH_FORCE_TERMINAL"] = "false"
    os.environ["NO_COLOR"] = "1"
    
    # Try to monkey-patch Rich if it's already imported
    try:
        import rich
        import rich.console
        import rich.pretty
        
        # Disable pretty printing
        rich.pretty.install = lambda *args, **kwargs: None
        
        # Replace console with a safe version
        class SafeConsole:
            def print(self, *args, **kwargs):
                # Fallback to regular print
                print(*args)
            
            def log(self, *args, **kwargs):
                print(*args)
                
            def inspect(self, *args, **kwargs):
                print(f"<object: {type(args[0]).__name__}>")
        
        # Replace Rich console instances
        rich.console.Console = SafeConsole
        
    except ImportError:
        # Rich not imported yet, which is fine
        pass


def safe_repr(obj: Any, max_length: int = 100) -> str:
    """Safely represent an object without triggering Rich recursion."""
    try:
        if obj is None:
            return "None"
        elif isinstance(obj, (str, int, float, bool)):
            result = repr(obj)
            return result[:max_length] + "..." if len(result) > max_length else result
        elif isinstance(obj, (list, tuple)):
            if len(obj) == 0:
                return "[]" if isinstance(obj, list) else "()"
            elif len(obj) > 5:
                return f"<{type(obj).__name__} with {len(obj)} items>"
            else:
                items = [safe_repr(item, 20) for item in obj[:3]]
                return f"[{', '.join(items)}{'...' if len(obj) > 3 else ''}]"
        elif isinstance(obj, dict):
            if len(obj) == 0:
                return "{}"
            elif len(obj) > 5:
                return f"<dict with {len(obj)} keys>"
            else:
                items = [f"{safe_repr(k, 20)}: {safe_repr(v, 20)}" for k, v in list(obj.items())[:3]]
                return f"{{{', '.join(items)}{'...' if len(obj) > 3 else ''}}}"
        else:
            return f"<{type(obj).__name__}>"
    except Exception:
        return f"<{type(obj).__name__}: unprintable>"


def safe_format_exception(exc: Exception) -> Dict[str, Any]:
    """Safely format exception information without circular references."""
    try:
        return {
            "type": type(exc).__name__,
            "message": str(exc)[:500],  # Truncate long messages
            "module": getattr(type(exc), "__module__", "unknown"),
        }
    except Exception:
        return {
            "type": "Exception",
            "message": "Unable to format exception",
            "module": "unknown",
        }


def safe_format_request(request) -> Dict[str, Any]:
    """Safely format request information without circular references."""
    try:
        result = {
            "method": "unknown",
            "path": "unknown",
            "client": "unknown",
        }
        
        if hasattr(request, 'method'):
            result["method"] = str(request.method)
        
        if hasattr(request, 'url') and hasattr(request.url, 'path'):
            result["path"] = str(request.url.path)
        
        if hasattr(request, 'client') and hasattr(request.client, 'host'):
            result["client"] = str(request.client.host)
        
        if hasattr(request, 'headers'):
            # Only include safe headers
            safe_headers = {}
            for key, value in request.headers.items():
                if key.lower() not in ['authorization', 'cookie', 'x-api-key', 'x-auth-token']:
                    safe_headers[key] = str(value)[:100]
            result["headers_count"] = len(request.headers)
            result["content_type"] = safe_headers.get("content-type", "unknown")
        
        return result
    except Exception:
        return {
            "method": "unknown",
            "path": "unknown", 
            "client": "unknown",
            "error": "Failed to format request"
        }


# Initialize protection on import
disable_rich_completely()