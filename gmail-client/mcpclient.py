import asyncio, json
from typing import Optional
from contextlib import AsyncExitStack

from gmail_credentials import get_access_token

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.openAI = OpenAI()
        self.access_token = get_access_token()
    
    async def connect_to_server(self, server_script_path: str):
        """
        Connect to the MCP server.
        """
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )
        
        # Get the file descriptor for the MCP server and make a session.
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()
        
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print(tools)
        print("\nConnected to Gmail MCP Server with tools", [tool.name for tool in tools])
        
    async def chat_loop(self):
        """
        Run an interactive chat loop
        """
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """
        Clean up resources
        """
        await self.exit_stack.aclose()
        
    async def process_query(self, query: str) -> str:
        """
        Process a query using Claude and available tools
        """
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        # List available tools
        response = await self.session.list_tools()
        available_tools = [{
            "type": "function",
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": {}
            }
        } for tool in response.tools]

        # Initial GPT API call to get the tools needed for the query.
        response = self.openAI.responses.create(
            model="gpt-4o-mini",
            input=messages,
            tools=available_tools
        )

        print(response)
        # Process response and handle tool calls
        final_text = []

        assistant_message_content = []
        if response.output_text:
            final_text.append(response.output_text)
            assistant_message_content.append(response.output_text)
        elif response.output:
            next_step = None
            
            for item in response.output:
                if item.type == 'function_call':
                    next_step = item
                
            if next_step is None:
                return
                        
            tool_name = next_step.name
            tool_args = json.loads(next_step.arguments)
            # Inject access_token automatically - LLM never sees this
            tool_args["access_token"] = self.access_token

            # Execute tool call
            result = await self.session.call_tool(tool_name, tool_args)
            final_text.append(f"[Calling tool {tool_name}]")

            # Don't include the function call object - just send the tool result as text
            # The API already knows what tool was called
            messages.append({
                "role": "user",
                "content": f"Tool {tool_name} returned: {str(result)}"
            })

            # Get next response from OpenAI
            response = self.openAI.responses.create(
                model="gpt-4o-mini",
                input=messages,
                tools=available_tools
            )

            final_text.append(response.output_text)

        return "\n".join(final_text)