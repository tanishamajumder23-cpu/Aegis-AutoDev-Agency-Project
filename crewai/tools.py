from functools import wraps


def tool(name: str):
    """Simple tool decorator stub for local CrewAI emulation."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        wrapper.tool_name = name
        return wrapper
    return decorator
