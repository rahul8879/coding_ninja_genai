from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
from pydantic import BaseModel, Field

class SupportState(TypedDict):
    customer_query: str
    query_category: str
    response: str 
    tools_used: list[str]

llm = ChatOpenAI(model="gpt-4o")

# Define structured output for classification
class QueryClassification(BaseModel):
    category: Literal["billing", "technical", "refund", "general"]
    confidence: float = Field(description="Confidence score 0-1")
    reasoning: str = Field(description="Why this category was chosen")


def classify_query(state: SupportState) -> SupportState:
    print("\n ROUTER: Analyzing customer query...")

    classifier_llm = llm.with_structured_output(QueryClassification)

    prompt = f"""Classify the following customer support query into one of these categories:
    
    - billing: Questions about invoices, payments, charges, pricing
    - technical: Technical issues, bugs, feature problems, integration issues  
    - refund: Refund requests, returns, cancellations
    - account: Account access, password reset, profile changes, login issues
    - general: General questions, feature inquiries, information requests

    Customer Query: {state['customer_query']}

    Classify accurately based on the primary intent."""

    classification = classifier_llm.invoke(prompt)

    print(f"Category: {classification.category}")
    print(f"Confidence: {classification.confidence: .2f}")
    print(f"Reasoning: {classification.reasoning}\n")

    return {
        "query_category": classification.category
    }


def handle_billing(state: SupportState) -> SupportState:

    print("💳 BILLING HANDLER: Processing billing query")

    prompt = f"""You are a billing specialist. Handle this customer query:

    {state['customer_query']}

    Provide a helpful response that:
    - References billing policies and procedures
    - Offers to check their account details
    - Provides clear next steps
    - Mentions relevant payment options

    Keep it professional and reassuring."""

    response = llm.invoke(prompt).content

    print("✅ BILLING HANDLER: Response Generated")

    return {
        "response": response,
        "tools_used": ["billing_database", "payment_processor"]
    }

def handle_technical(state: SupportState) -> SupportState:

    print("🛠️ TECHNICAL HANDLER: Processing technical query")

    prompt = f"""You are a technical support specialist. Handle this customer query:

    {state['customer_query']}

    Provide a helpful response that:
    - Offers specific troubleshooting steps
    - References relevant documentation
    - Asks clarifying questions if needed
    - Provides workarounds if applicable

    Be clear and technical but accessible."""

    response = llm.invoke(prompt).content

    print("✅ TECHNICAL HANDLER: Response Generated")

    return {
        "response": response,
        "tools_used": ["knowledge_base", "bug_tracker", "system_logs"]
    }

def handle_refund(state: SupportState) -> SupportState:

    print("💰 REFUND HANDLER: Processing refund query")

    prompt = f"""You are a refund specialist. Handle this customer query:

    {state['customer_query']}

    Provide a helpful response that:
    - Explains the refund policy clearly
    - Outlines the refund process and timeline
    - Asks for necessary information (order number, reason, etc.)
    - Shows empathy and understanding

    Be empathetic and solution-focused."""

    response = llm.invoke(prompt).content

    print("✅ REDUND HANDLER: Response Generated")

    return {
        "response": response,
        "tools_used": ["order_database", "refund_processor"]
    }

def handle_general(state: SupportState) -> SupportState:
    """Handle general queries"""
    print("ℹ️  GENERAL HANDLER: Processing general inquiry...")
    
    prompt = f"""You are a general support specialist. Handle this customer query:

    {state['customer_query']}

    Provide a helpful response that:
    - Answers their question clearly
    - Provides relevant links or resources
    - Offers additional help if needed
    - Suggests related features they might find useful

    Be friendly and informative."""
    
    response = llm.invoke(prompt).content
    
    print("✓ GENERAL HANDLER: Response generated\n")
    
    return {
        "response": response,
        "tools_used": ["knowledge_base", "faq_database"]
    }


def route_query(state: SupportState) -> Literal["billing", "technical", "refund", "general"]:
    print(f"🚏 ROUTING: Directing to {state['query_category']} handler...\n")

    return state['query_category']


builder = StateGraph(SupportState)

builder.add_node("classify_query", classify_query)
builder.add_node("billing", handle_billing)
builder.add_node("technical", handle_technical)
builder.add_node("refund", handle_refund)
builder.add_node("general", handle_general)

builder.add_edge(START, "classify_query")

builder.add_conditional_edges(
    "classify_query",
    route_query,
    {
        "billing": "billing",
        "technical": "technical",
        "refund": "refund",
        "general": "general"
    }
)

builder.add_edge("billing", END)
builder.add_edge("technical", END)
builder.add_edge("refund", END)
builder.add_edge("general", END)

graph = builder.compile()

# Example Prompts
billing_prompt = "I was charged twice for my subscription this month. Can you help?"
technical_prompt = "The app keeps crashing when I try to upload files larger than 10MB."
refund_prompt = "I'd like to request a refund for my recent purchase. It doesn't meet my needs."
general_prompt = "What features are included in the Pro plan?"


result = graph.invoke({
    "customer_query": technical_prompt,
    "query_category": "",
    "response": "",
    "tools_used": ""
})

print("="* 70)
print(f"FINAL RESPONSE ({result['query_category'].upper()})")
print("="* 70)
print(result["response"])
print(f"\n🔧 Tools Used: {','.join(result['tools_used'])}")