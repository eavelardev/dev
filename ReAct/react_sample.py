from langgraph.graph import StateGraph, START, END, MessagesState
from langchain.messages import SystemMessage, HumanMessage, ToolMessage
from langchain.tools import tool
# Define tools
@tool
def multiply(a: int, b: int) -> int:
   return a * b
@tool
def add(a: int, b: int) -> int:
   return a + b
tools = [add, multiply]
tools_by_name = {t.name: t for t in tools}
# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)
# Agent node: decides next action
def llm_call(state: MessagesState):
   return {
       "messages": [
           llm_with_tools.invoke(
               [SystemMessage(content="You are a helpful math assistant.")] + state["messages"]
           )
       ]
   }
# Tool execution node
def tool_node(state: dict):
   results = []
   for call in state["messages"][-1].tool_calls:
       tool_fn = tools_by_name[call["name"]]
       output = tool_fn.invoke(call["args"])
       results.append(ToolMessage(content=output, tool_call_id=call["id"]))
   return {"messages": results}
# Routing logic
def should_continue(state: MessagesState):
   if state["messages"][-1].tool_calls:
       return "tool_node"
   return END
# Build the graph
builder = StateGraph(MessagesState)
builder.add_node("llm_call", llm_call)
builder.add_node("tool_node", tool_node)
builder.add_edge(START, "llm_call")
builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
builder.add_edge("tool_node", "llm_call")
agent = builder.compile()
# Run the agent
messages = [HumanMessage(content="Add 3 and 4.")]
result = agent.invoke({"messages": messages})
for m in result["messages"]:
   m.pretty_print()