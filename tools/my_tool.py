from collections.abc import Callable
from typing import Any


class MyTool:
    """
    A class representing a reusable piece of code (Tool).

    Attributes:
        name (str): Name of the tool.
        description (str): A textual description of what the tool does.
        func (callable): The function this tool wraps.
        arguments (list): A list of arguments.
        outputs (str or list): The return type(s) of the wrapped function.
    """

    def __init__(
        self, name: str, description: str, func: Callable, outputs: str, arguments: list
    ):
        self.name = name
        self.description = description
        self.func = func
        self.outputs = outputs
        self.arguments = arguments

    def to_string(self):
        """
        Return a string representation of the tool,
        including its name, description, arguments, and outputs.
        """

        args_str = ", ".join(
            [f"{arg_name}: {arg_type}" for arg_name, arg_type in self.arguments]
        )

        return (
            f"Tool Name: {self.name},"
            f" Description: {self.description},"
            f" Arguments: {args_str},"
            f" Outputs: {self.outputs}"
        )

    def __call__(self, *args, **kwds):
        """
        Invoke the underlying function (callable) with provided arguments.
        """
        return self.func(*args, **kwds)

    def to_open_ai_tools(self) -> dict[str, Any]:
        properties = {}

        for arg_name, arg_type in self.arguments:
            json_types = {
                "int": "integer",
                "float": "number",
                "str": "string",
                "bool": "boolean",
            }.get(arg_type, "string")

            properties[arg_name] = {"type": json_types}

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": list(properties.keys()),
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }
