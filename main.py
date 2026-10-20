import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolUnionParam

from tools.calculator import add, divide, multiple, sub

load_dotenv()

api_key = os.environ.get("OPEN_ROUTER_KEY", "")
if api_key == "":
    raise ValueError("api key not found")

open_router_base_url = os.environ.get("OPEN_ROUTER_BASE_URL", "")
if open_router_base_url == "":
    raise ValueError("open router url is required!")


def main():
    client = OpenAI(api_key=api_key, base_url=open_router_base_url)

    calculator_tools = [multiple, divide, add, sub]
    available_tools = {item.name: item for item in calculator_tools}

    tools: list[ChatCompletionToolUnionParam] = [
        item.to_open_ai_tools() for item in calculator_tools
    ]

    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": "Your name is Sylla",
        },
    ]

    while True:
        q = str(input("Tanya apa saja: "))

        if q.lower() == "exit":
            print("bye!")
            break

        messages.append({"role": "user", "content": q})

        while True:
            stream = client.chat.completions.create(
                model="nvidia/nemotron-3-ultra-550b-a55b:free",
                messages=messages,
                tools=tools,
                stream=True,
                tool_choice="auto",
            )

            assistant_content: list[str] = []
            streamed_tool_calls = {}

            for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                if delta.content:
                    assistant_content.append(delta.content)
                    print(delta.content, end="", flush=True)

                for tool_delta in delta.tool_calls or []:
                    tool_call = streamed_tool_calls.setdefault(
                        tool_delta.index,
                        {
                            "id": "",
                            "name": "",
                            "arguments": "",
                        },
                    )

                    if tool_delta.id:
                        tool_call["id"] = tool_delta.id

                    if tool_delta.function:
                        if tool_delta.function.name:
                            if not tool_call["name"]:
                                print(
                                    f"\n[Memanggil tool: {tool_delta.function.name}]",
                                    flush=True,
                                )
                            tool_call["name"] = tool_delta.function.name

                        if tool_delta.function.arguments:
                            tool_call["arguments"] += tool_delta.function.arguments
                            print(".", end="", flush=True)

            assistant_tool_calls = [
                {
                    "id": tool_call["id"],
                    "type": "function",
                    "function": {
                        "name": tool_call["name"],
                        "arguments": tool_call["arguments"],
                    },
                }
                for _, tool_call in sorted(streamed_tool_calls.items())
            ]

            assistant_message = {
                "role": "assistant",
                "content": "".join(assistant_content) or None,
            }

            if assistant_tool_calls:
                assistant_message["tool_calls"] = assistant_tool_calls

            messages.append(assistant_message)

            if not assistant_tool_calls:
                if not assistant_content:
                    print("(Tidak ada output)", end="")
                print()
                break

            for tool_call in assistant_tool_calls:
                function_name = tool_call["function"]["name"]
                selected_tool = available_tools.get(function_name)

                if selected_tool is None:
                    raise ValueError(f"Tool tidak ditemukan: {function_name}")

                print(f"\n[Menjalankan {function_name}...]", flush=True)
                function_arguments = json.loads(tool_call["function"]["arguments"])
                result = selected_tool(**function_arguments)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": str(result),
                    }
                )

        print()
        print(json.dumps(messages, indent=2))


if __name__ == "__main__":
    main()
