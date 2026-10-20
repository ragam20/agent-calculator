from collections.abc import Callable
import inspect
from typing import Any

from .my_tool import MyTool


def tool(func: Callable[..., Any]) -> MyTool:
    """
    A decorator that creates a Tool instance from the given function.
    """

    # Get the function signature
    sign = inspect.signature(func)

    # Extract (param_name, param_annotation) pairs for input
    arguments = []
    for param in sign.parameters.values():
        annotation_name = (
            param.annotation.__name__
            if hasattr(param.annotation, "__name__")
            else str(param.annotation)
        )
        arguments.append((param.name, annotation_name))

    # Determine the return annotation
    return_annotation = sign.return_annotation
    if return_annotation is inspect._empty:
        outputs = "No return annotation"
    else:
        outputs = (
            return_annotation.__name__
            if hasattr(return_annotation, "__name__")
            else str(return_annotation)
        )

    # Use the function's docstring as the description (default if None)
    description = func.__doc__ or "No  description provided."

    # The function name becomes the Tool Name
    name = func.__name__

    # Return a new Tool instance
    return MyTool(
        name=name,
        description=description,
        func=func,
        outputs=outputs,
        arguments=arguments,
    )
