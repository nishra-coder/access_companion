import os
from typing import Annotated, TypedDict, List
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# 1. MODELS - Switched to 2.5 Flash for better stability and API compatibility
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    google_api_key=api_key, 
    temperature=0.2
)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001", 
    google_api_key=api_key
)

vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# 2. STATE DEFINITION
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The chat history"]
    context: str
    intent: str 

# 3. AGENT NODES
def router_node(state: AgentState):
    last_msg = state['messages'][-1].content.lower()
    
    # Bypass for clear greetings/identities
    if any(word in last_msg for word in ["hi", "hello", "wassup", "who are you"]):
        return {"intent": "social"}
    
    prompt = f"Is this a query about computer tasks or screen readers? Respond only 'technical' or 'social'. Input: {last_msg}"
    response = llm.invoke(prompt).content.lower()
    return {"intent": "technical" if "technical" in response else "social"}

def knowledge_node(state: AgentState):
    """Retrieves NVDA manual context."""
    if state['intent'] == "social":
        return {"context": ""}
    
    # Query using last 2 messages for thread context
    query_text = " ".join([m.content for m in state['messages'][-2:]])
    docs = vectorstore.similarity_search(query_text, k=3)
    return {"context": "\n\n".join([d.page_content for d in docs])}

def assistant_node(state: AgentState):
    """The Vispero-style response generator."""
    
    system_prompt = (
        "You are AccessCompanion, an assistant for visually impaired users using NVDA. "
        "Your goal is to provide specific, step-by-step guidance.\n\n"
        "STRICT INSTRUCTIONS:\n"
        "1. ALWAYS frame answers within the context of using the NVDA screen reader.\n"
        "2. If the user asks for a general task (e.g., 'Make a Google account'), provide "
        "instructions using NVDA commands like 'Tab to navigate', 'Enter to activate', etc.\n"
        "3. Provide shortcuts clearly (e.g., NVDA Key + N).\n"
        "4. Use numbered lists for steps. Be direct and avoid fluff.\n"
        "5. If a user asks for weather or general trivia, politely decline and say you "
        "are here to assist with NVDA and accessibility."
    )
    
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(state['messages'])
    
    if state['context']:
        messages.append(SystemMessage(content=f"NVDA Manual Reference: {state['context']}"))
    
    response = llm.invoke(messages)
    return {"messages": [response]}

# 4. THE GRAPH
builder = StateGraph(AgentState)
builder.add_node("router", router_node)
builder.add_node("knowledge", knowledge_node)
builder.add_node("assistant", assistant_node)

builder.add_edge(START, "router")
builder.add_edge("router", "knowledge")
builder.add_edge("knowledge", "assistant")
builder.add_edge("assistant", END)

app = builder.compile(checkpointer=InMemorySaver())

# 5. CHAT
def start_chat():
    config = {"configurable": {"thread_id": "access_companion_stable"}}
    print("\n--- AccessCompanion (NVDA Edition) Active ---")
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]: break
            
            for event in app.stream({"messages": [HumanMessage(content=user_input)]}, config):
                if "assistant" in event:
                    print(f"\nCompanion: {event['assistant']['messages'][-1].content}\n")
        except Exception as e:
            print(f"\nError: {e}")
            break

if __name__ == "__main__":
    start_chat()