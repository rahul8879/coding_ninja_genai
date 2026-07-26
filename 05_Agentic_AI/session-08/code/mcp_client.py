import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition, ToolNode
from typing import Annotated, List
from typing_extensions import TypedDict
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_mcp_adapters.tools import load_mcp_tools

# MCP server launch config
server_params = StdioServerParameters(
    command="python",
    args=["weather_server.py"]
)

# LangGraph state definition
class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


async def create_graph(session):
    # Load tools from MCP server
    
    tools = await load_mcp_tools(session)

    # LLM configuration 
    llm = ChatOpenAI(model="gpt-4o-mini")
    llm_with_tools = llm.bind_tools(tools)

    # Prompt template with user/assistant chat only
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that uses tools to get the current weather for a location."),
        MessagesPlaceholder("messages")
    ])

    chat_llm = prompt_template | llm_with_tools

    # Define chat node
    def chat_node(state: State) -> State:
        state["messages"] = chat_llm.invoke({"messages": state["messages"]})
        return state

    # Build LangGraph with tool routing
    graph = StateGraph(State)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tool_node", ToolNode(tools=tools))
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition, {
        "tools": "tool_node",
        "__end__": END
    })
    graph.add_edge("tool_node", "chat_node")

    return graph.compile(checkpointer=MemorySaver())


# Entry point
async def main():
    """
    Main async function that orchestrates the entire MCP (Model Context Protocol) weather agent.
    This function handles:
    1. Establishing connection to the MCP server
    2. Initializing the client session for tool use
    3. Creating the agent graph with LangGraph
    4. Running the interactive loop for user queries
    """
    
    # ============================================================================
    # INITIALIZATION PART - MCP Server Connection & Session Setup
    # ============================================================================
    
    # Step 1: Create stdio_client context manager for MCP communication
    # - stdio_client connects to the MCP server over standard input/output
    # - server_params contains MCP server configuration (command, args, etc.)
    # - This context manager automatically handles connection lifecycle
    # - When we exit the 'async with' block, it safely closes the connection
    async with stdio_client(server_params) as (read, write):
        # read: async reader to receive messages from MCP server
        # write: async writer to send messages to MCP server
        
        # Step 2: Create ClientSession for MCP interaction
        # - ClientSession handles the request-response protocol with MCP server
        # - It wraps the read/write streams we got from stdio_client
        # - This allows us to make structured requests and get responses
        # - Example: {"jsonrpc": "2.0", "method": "tools/list", ...}
        async with ClientSession(read, write) as session:
            
            # Step 3: Initialize the MCP session
            # - This sends "initialize" request to MCP server
            # - Server responds with capabilities (tools it provides)
            # - Must be called before we can use any tools
            # - Establishes that both client and server are ready to communicate
            await session.initialize()
            # After this line:
            # - MCP connection is active
            # - We know what tools are available
            # - Server is ready to handle tool calls
            
            # ================================================================
            # AGENT CREATION PART
            # ================================================================
            
            # Step 4: Create the LangGraph agent
            # - create_graph() builds our agent using LangGraph framework
            # - Passes the initialized MCP session so agent can call tools
            # - Returns a compiled graph (LangGraph's CompiledGraph object)
            # - The graph contains: nodes (reasoning steps) + edges (transitions)
            # - LLM decides which tools to call based on user query
            agent = await create_graph(session)
            
            # Confirmation message to user
            print("Weather MCP agent is ready.")
            
            # ================================================================
            # MAIN INTERACTIVE LOOP
            # ================================================================
            
            # Infinite loop for conversational interaction
            while True:
                # Step 5: Get user input from command line
                # - input() is blocking/synchronous (pauses for user input)
                # - .strip() removes leading/trailing whitespace
                user_input = input("\nYou: ").strip()
                
                # Step 6: Check if user wants to exit
                # - Allows multiple ways to exit: "exit", "quit", or "q"
                # - .lower() makes the check case-insensitive
                if user_input.lower() in {"exit", "quit", "q"}:
                    # Break out of the while loop, ending the conversation
                    break
                
                # Step 7: Try-except block for error handling
                # - If agent fails, we catch the error and continue
                # - Without this, one bad query would crash the entire program
                try:
                    # Step 8: Invoke the agent (main reasoning step)
                    # - ainvoke: "async invoke" - calls the agent asynchronously
                    # - {"messages": user_input}: Input structure for the agent
                    #   - Creates a LangChain HumanMessage from user_input
                    #   - Agent will process this and call tools if needed
                    response = await agent.ainvoke(
                        {"messages": user_input},
                        # config dictionary for agent behavior control
                        config={
                            "configurable": {
                                # thread_id: Enables state persistence & memory
                                # - Same thread_id = same conversation context
                                # - Agent remembers previous messages in this thread
                                # - Allows multi-turn conversations with context
                                # - "weather-session" is our thread identifier
                                "thread_id": "weather-session"
                            }
                        }
                    )
                    # After ainvoke completes:
                    # - response["messages"] contains list of all messages
                    # - Last message is the agent's final response
                    # - Previous messages are context (we asked about weather)
                    # - Tools may have been called and results included
                    
                    # Step 9: Extract and display the agent's response
                    # - response["messages"] is a list of message objects
                    # - response["messages"][-1] gets the LAST message (newest)
                    # - .content gets the text content of that message
                    # - This is what we display to the user
                    print("AI:", response["messages"][-1].content)
                    
                # Step 10: Catch any errors that occur during agent execution
                except Exception as e:
                    print("Error:", e)
            
     

if __name__ == "__main__":
    asyncio.run(main())