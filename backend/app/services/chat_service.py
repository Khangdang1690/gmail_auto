import asyncio
from typing import Dict, Any, List, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID

# Define the state structure for our LangGraph
class ChatState(TypedDict):
    messages: List[BaseMessage]
    current_response: str
    model_id: str
    session_id: str

# LangGraph nodes
async def chat_node(state: ChatState) -> ChatState:
    """Main chat processing node using OpenAI"""
    model = ChatOpenAI(
        temperature=0.8,
        model=state["model_id"],
        streaming=True
    )
    
    # Get the response from the model
    response = await model.ainvoke(state["messages"])
    
    # Add the AI response to messages
    updated_messages = state["messages"] + [response]
    
    return {
        **state,
        "messages": updated_messages,
        "current_response": response.content
    }

def create_chat_graph() -> StateGraph:
    """Create and configure the LangGraph for chat processing"""
    
    # Define the graph state
    graph = StateGraph(ChatState)
    
    # Add nodes
    graph.add_node("chat", chat_node)
    
    # Define the flow
    graph.set_entry_point("chat")
    graph.add_edge("chat", END)
    
    return graph.compile()

async def process_chat(model_id: str, messages, db: Session, chat_session_id: UUID):
    """
    Process chat using LangGraph for more complex workflows
    """
    # Convert messages to LangChain format
    langchain_messages = []
    for msg in messages:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            langchain_messages.append(AIMessage(content=msg.content))
    
    # Create the chat graph
    chat_graph = create_chat_graph()
    
    # Initialize state
    initial_state: ChatState = {
        "messages": langchain_messages,
        "current_response": "",
        "model_id": model_id,
        "session_id": str(chat_session_id)
    }
    
    async def generate_chat_responses():
        from app.models import Message
        
        full_response = ""
        try:
            # For streaming, we'll use the model directly with streaming
            model = ChatOpenAI(
                temperature=0.8,
                model=model_id,
                streaming=True
            )
            
            async for chunk in model.astream(langchain_messages):
                if hasattr(chunk, 'content') and chunk.content:
                    full_response += chunk.content
                    # Stream the chunk to the client
                    yield f'0:"{chunk.content}"\n'
                    
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            # Save the accumulated response to the database
            if full_response:
                db.add(Message(
                    chat_session_id=chat_session_id,
                    role="assistant",
                    content=full_response
                ))
                db.commit()

    response = StreamingResponse(generate_chat_responses())
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return response

# Future: Add more complex nodes for different capabilities
async def tool_node(state: ChatState) -> ChatState:
    """Node for tool/function calling (for future use)"""
    # This is where you'd add tool calling logic
    return state

async def memory_node(state: ChatState) -> ChatState:
    """Node for conversation memory management (for future use)"""
    # This is where you'd add memory/context management
    return state
