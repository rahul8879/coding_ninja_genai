"""
Task: Content Generation pipeline with Quality Control

Input:
- Topic
- Quality Requirements

Steps:
- Generate an initial draft
- Fact check the draft
- Improve the draft based on recommendations from the previous step
- Format for publication
"""

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class ContentState(TypedDict):
    topic: str
    requirements: str
    draft: str
    fact_check_results: str
    improved_content: str
    final_draft: str

llm = ChatOpenAI(model="gpt-4o")


# Define Nodes
def generate_draft(state: ContentState) -> ContentState:
    """Generate intial blog post draft"""

    prompt = f"""
        Write a 200-word blog post about : {state['topic']}

        Requirements: {state['requirements']}

        Focus on creating engaging, informative content
    """

    draft = llm.invoke(prompt).content

    print("=== STEP 1: Draft Generated ===")
    print(draft[:150] +"....\n")

    return {
        "draft": draft
    }

def fact_check(state: ContentState) -> ContentState:
    """Check draft for factual accuracy and consistency"""

    prompt = f"""
    Review the following blog post draft for factual accuracy and consistency:
    
    {state['draft']}

    Identify:
    1. Any factual claims that seem questionable
    2. Internal inconsistencies
    3. Statements that need citations

    Provide a brief report."""

    fact_check_results = llm.invoke(prompt).content

    print("=== STEP 2: Fact Check Complete ===")
    print(fact_check_results[:150] +"....\n")

    return {
        "fact_check_results": fact_check_results
    }

def improve_content(state: ContentState) -> ContentState:
    """Revise content based on fact check feedback"""

    prompt = f"""
    Here is a blog post draft:

    {state['draft']}

    Here is feedback from fact-checking:

    {state['fact_check_results']}

    Revise the blog post to address the feedback while maintaining engaging writing. Keep it around 200 words."""

    improved = llm.invoke(prompt).content

    print("=== STEP 3: Content Improved ===")
    print(improved[:150] +"....\n")

    return {
        "improved_content": improved
    }

def format_output(state: ContentState) -> ContentState:
    """Format content with HTML tags and elements"""

    prompt = f"""
    Format the following blog post for web publication:

    {state['improved_content']}

    Add:
    - An engaging title wrapped in <h1> tags
    - Subheadings where appropriate with <h2> tags
    - Paragraph tags <p>
    - A meta description (1-2 sentences)

    Output the formatted HTML."""

    final = llm.invoke(prompt).content

    print("=== STEP 4: Formatted for Publication ===")
    print(final[:200] +"....\n")

    return {
        "final_draft": final
    }


builder = StateGraph(ContentState)

builder.add_node(generate_draft)
builder.add_node(fact_check)
builder.add_node(improve_content)
builder.add_node(format_output)

# Build the prompt-chaining flow

builder.add_edge(START, "generate_draft")
builder.add_edge("generate_draft", "fact_check")
builder.add_edge("fact_check", "improve_content")
builder.add_edge("improve_content", "format_output")
builder.add_edge("format_output", END)

graph = builder.compile()

result = graph.invoke({
    "topic": "The benefits of morning exercise",
    "requirements": "Target audience: busy professionals. Include practicals"
})


print("\n" + "="*50)
print("FINAL RESULT")
print("="*50)
print(result["final_draft"])

