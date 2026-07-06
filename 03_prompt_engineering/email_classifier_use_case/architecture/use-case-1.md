# Assignment — Use Case 3: E-Commerce Review Intelligence
## GenAI Course · Sessions 3–6 Capstone Assignment

---

## Overview

You are building an **AI-powered review analysis system** for an e-commerce seller.

The seller receives 500–2000 customer reviews every day on platforms like Flipkart and Amazon. Reading them manually is impossible. Your job is to build a pipeline that automatically reads, understands, and extracts structured intelligence from every review — overnight, in bulk, at near-zero cost.

**This is a real product.** Everything you build here maps directly to a production system a startup would ship.

---

## Problem Statement

A seller selling phone accessories on Flipkart gets 1000+ reviews per day.

**Current situation (without AI):**
- A support executive reads reviews manually — 2–3 hours per day
- Urgent complaints (safety issues, defective batch) get noticed 2–3 days late
- No trend visibility — are complaints about the charging cable increasing or decreasing?
- No time to reply to negative reviews individually

**Your task:** Replace this manual process with an automated LangChain pipeline.

---

## What You Will Build

A Python script or Jupyter notebook that takes a list of customer reviews and produces structured analysis for each one.

### Input

```python
reviews = [
    {
        "review_id": "R001",
        "product": "USB-C Fast Charging Cable 2m",
        "rating": 2,
        "text": "Bought this 3 weeks ago. The cable stopped working after just 10 days. The connector gets very hot during charging which is dangerous. Worst purchase ever. Demanding a full refund."
    },
    {
        "review_id": "R002",
        "product": "USB-C Fast Charging Cable 2m",
        "rating": 5,
        "text": "Excellent build quality! Charges my phone from 0 to 100 in 45 minutes. The braided design looks premium and feels durable. Using it daily for 2 months, no issues at all."
    },
    {
        "review_id": "R003",
        "product": "USB-C Fast Charging Cable 2m",
        "rating": 3,
        "text": "Charging speed is good but the cable length is a bit short for my setup. Also the connector is slightly loose in my phone port. Decent for the price though."
    },
    {
        "review_id": "R004",
        "product": "USB-C Fast Charging Cable 2m",
        "rating": 1,
        "text": "SCAM PRODUCT. This is not fast charging at all. Same speed as a normal cable. The product images are misleading. I will be filing a complaint with consumer court if no action is taken."
    },
    {
        "review_id": "R005",
        "product": "USB-C Fast Charging Cable 2m",
        "rating": 4,
        "text": "Pretty good cable. Fast charging works well with my Samsung. Build quality seems solid. Only complaint is the packaging could be better — box was damaged when delivered."
    }
]
```

### Expected Output (for each review)

```python
ReviewAnalysis(
    review_id="R001",
    sentiment="Negative",
    confidence=0.97,
    features=["connector heating", "cable durability", "charging speed"],
    summary="Cable stopped working after 10 days with dangerous connector overheating.",
    urgent=True,
    urgency_reason="Safety concern: connector overheating reported. Potential product defect.",
    suggested_reply="We sincerely apologize for this experience. Connector overheating is a serious concern and we are escalating this immediately. Please DM us your order ID for a full refund and replacement."
)
```

---

## Part 1 — Pydantic Output Model (10 marks)

Define the output model for a single review analysis.

### Task

Create a Pydantic `BaseModel` called `ReviewAnalysis` with the following fields:

| Field | Type | Constraint | Description for LLM |
|-------|------|-----------|------------|
| `review_id` | `str` | required | ID passed through from input |
| `sentiment` | `Literal` | Positive / Negative / Mixed | Overall tone of the review |
| `confidence` | `float` | 0.0 to 1.0 | How confident are you in this sentiment? |
| `features` | `List[str]` | min 1 item | Product features the customer mentions |
| `summary` | `str` | max 200 chars | 1–2 sentence summary of the review |
| `urgent` | `bool` | default False | Does this need immediate human attention? |
| `urgency_reason` | `Optional[str]` | default None | Why is it urgent? Only set if urgent=True |
| `suggested_reply` | `str` | max 400 chars | Draft reply to send to this customer |

### Starter Code

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, List, Optional

class ReviewAnalysis(BaseModel):
    # TODO: Define all 8 fields with proper Field(description="...")
    pass
```

### Requirements

1. Every field must have a `description` in `Field()` — this description gets sent to the LLM
2. Add a `@field_validator` that normalises `sentiment` — accept "positive", "POSITIVE", "Positive" all as "Positive"
3. Add a `@model_validator(mode="after")` that:
   - Raises `ValueError` if `urgent=True` but `urgency_reason` is None or empty
   - Auto-sets `urgent=True` if the summary contains any of these words: "safety", "fire", "burn", "explode", "court", "complaint", "dangerous"

---

## Part 2 — Four Analysis Chains (40 marks)

Build 4 separate LCEL chains. Each chain does exactly one job. All use the same LLM.

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import PydanticOutputParser

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

---

### Chain 1 — Sentiment Chain (10 marks)

**Session concept: Chain-of-Thought (Session 4)**

The LLM must reason step-by-step before giving the label. Do not ask for the answer directly — ask it to think first.

**Your prompt must include these CoT steps:**
1. What is the main emotion in this review?
2. What specific words signal that emotion?
3. Based on steps 1 and 2, what is the final sentiment?

**Output Pydantic model to create:**

```python
class SentimentResult(BaseModel):
    sentiment: Literal["Positive", "Negative", "Mixed"]
    confidence: float = Field(ge=0.0, le=1.0, description="...")
    reasoning: str = Field(description="Your step-by-step thinking")
```

**Chain:**

```python
sentiment_chain = sentiment_prompt | llm | PydanticOutputParser(pydantic_object=SentimentResult)
```

---

### Chain 2 — Feature Extraction Chain (10 marks)

**Session concept: Few-shot prompting (Session 3)**

Provide 2 examples in the prompt showing exactly what good feature extraction looks like. The LLM must only extract features that are actually mentioned in the review — no hallucination.

**Few-shot examples to include in your prompt:**

```
Review: "Great battery life but the screen is too dim and the buttons feel cheap"
Features: ["battery life", "screen brightness", "button quality"]

Review: "Delivery was fast but the product smells bad and packaging is terrible"
Features: ["delivery speed", "product smell", "packaging quality"]
```

**Output Pydantic model:**

```python
class FeatureResult(BaseModel):
    features: List[str] = Field(
        min_length=1,
        description="List of product features mentioned. Only features explicitly in the review."
    )
```

**Guardrail to add (Session 6):** Add a `@field_validator` that rejects any feature string longer than 40 characters — if the LLM returns a full sentence instead of a short feature name, catch it.

---

### Chain 3 — Summary Chain (10 marks)

**Session concept: Zero-shot + streaming (Sessions 3 and 6)**

Simple zero-shot prompt. The summary should be max 2 sentences and capture the most important point.

**Streaming requirement:** After running `.batch()` for all reviews, demonstrate `.stream()` on at least one review to show the summary appearing word by word. Add a `print(chunk, end="", flush=True)` loop.

**Output:** Plain `str` using `StrOutputParser()` — no Pydantic needed here.

**Self-imposed constraint:** Add a check after parsing — if `len(summary) > 200`, truncate to the last complete sentence under 200 characters.

---

### Chain 4 — Urgency Chain (10 marks)

**Session concept: Self-Consistency + Tree of Thought (Session 4)**

This is the most important chain — a false negative (missing a safety complaint) costs the seller their product listing.

**Self-Consistency requirement:** Run the urgency chain **3 times** on the same review. Flag as urgent only if **at least 2 out of 3 runs** return `urgent=True`. This reduces false positives and catches things a single pass might miss.

```python
# Run 3 times and take majority vote
runs = [urgency_chain.invoke({"review_text": review["text"]}) for _ in range(3)]
urgent = sum(r.urgent for r in runs) >= 2
```

**Tree of Thought prompt structure:** Your system prompt should walk through a decision tree:

```
Step 1: Does the review mention physical safety? (fire, burn, shock, explosion, injury)
        If YES → urgent=True, stop.
Step 2: Does the review contain legal threats? (court, complaint, consumer forum, FIR, police)
        If YES → urgent=True, stop.
Step 3: Does the review suggest a defective batch? (multiple units, batch, all units)
        If YES → urgent=True, stop.
Step 4: None of the above → urgent=False
```

**Output Pydantic model:**

```python
class UrgencyResult(BaseModel):
    urgent: bool
    urgency_reason: Optional[str] = Field(
        default=None,
        description="Required if urgent=True. Which step triggered it and why."
    )
    decision_path: str = Field(
        description="Which steps you evaluated and what you found at each step"
    )
```

---

## Part 3 — Batch Pipeline (30 marks)

### Task 3a — Run all 4 chains via `.batch()` (15 marks)

Process all 5 test reviews through all 4 chains in parallel.

```python
# Your pipeline should look roughly like this
def analyse_reviews(reviews: list[dict]) -> list[ReviewAnalysis]:
    inputs = [{"review_text": r["text"], "review_id": r["review_id"]} for r in reviews]

    # TODO: Run all 4 chains via .batch()
    # TODO: Merge results into ReviewAnalysis objects
    # TODO: Return list of ReviewAnalysis

    pass
```

Requirements:
- Use `.batch()` with `config={"max_concurrency": 3}` — do not use a for loop
- Merge the 4 chain outputs into one `ReviewAnalysis` Pydantic object per review
- Handle the case where Self-Consistency (3 urgency runs) happens inside the pipeline
- Print a summary table at the end:

```
Review ID   Sentiment    Urgent   Features Count   Summary (truncated)
R001        Negative     YES      3                Cable stopped working after 10 days...
R002        Positive     NO       4                Excellent build quality and fast charg...
R003        Mixed        NO       2                Good charging speed but cable length...
R004        Negative     YES      2                Product falsely advertised as fast cha...
R005        Positive     NO       2                Good fast charging cable with minor pa...
```

### Task 3b — Cost Tracking (Session 5) (10 marks)

After running the pipeline, print a cost report.

```python
# Expected output
Cost Report
-----------
Reviews processed  : 5
Total API calls    : 5 reviews x 4 chains x 3 urgency runs = 35 calls
Estimated tokens   : ~42,000 (input + output combined)
Estimated cost     : $0.0063  (at gpt-4o-mini pricing: $0.15/1M input, $0.60/1M output)
Cost per review    : $0.00126
Cost per 1000 rev  : $1.26
```

You can estimate tokens using `len(text.split()) * 1.3` as a rough approximation, or use the `usage_metadata` from the LLM response.

### Task 3c — Error Handling (Session 5) (5 marks)

Add `.with_retry(stop_after_attempt=3)` to every chain.

Handle `OutputParserException` — if the LLM returns malformed JSON, catch it gracefully and return a default `ReviewAnalysis` with:
- `sentiment="Mixed"`, `confidence=0.0`
- `summary="Parse error — manual review needed"`
- `urgent=False`

Do not let one bad parse crash the entire batch.

---

## Part 4 — Reflection Questions (20 marks)

Answer these in your notebook as markdown cells. 3–5 sentences each.

**Q1.** In Chain 4 (Urgency), why did we use Self-Consistency (3 runs, majority vote) instead of just running the chain once? What specific failure does this protect against? Give an example where a single run might give the wrong answer.

**Q2.** Compare the output parsing in Session 4 (manual `split("\n")`) vs Session 6 (PydanticOutputParser). What broke in the S4 approach? What specific problem does Pydantic solve that is not just about "cleaner code"?

**Q3.** Review R001 mentions a connector getting hot. A seller might want to suppress this review or delay responding. Should an AI system automatically escalate safety complaints even if the seller instructs otherwise? What is the role of guardrails here?

**Q4.** The cost per 1000 reviews is approximately Rs 10. A human doing this job costs Rs 30,000/month. However, there are things a human reviewer would catch that this pipeline would miss. Name 3 specific things and explain why the LLM would miss them.

**Q5.** You ran all 4 chains separately and then merged the outputs. An alternative design is to run one single chain that returns all 4 outputs at once. What are the tradeoffs of each approach? When would you choose one over the other?

---

## Submission Checklist

Before submitting, verify each item:

- [ ] `ReviewAnalysis` Pydantic model with all 8 fields and Field descriptions
- [ ] `@field_validator` for sentiment normalisation
- [ ] `@model_validator` for urgency_reason validation + auto-flag
- [ ] Chain 1 — CoT sentiment with 3-step reasoning in prompt
- [ ] Chain 2 — Few-shot feature extraction with 2 examples
- [ ] Chain 3 — Zero-shot summary with `.stream()` demo
- [ ] Chain 4 — Urgency with 3-run Self-Consistency + ToT decision tree prompt
- [ ] `.batch()` used (not a for loop) with `max_concurrency=3`
- [ ] Summary table printed
- [ ] Cost report printed
- [ ] `.with_retry(stop_after_attempt=3)` on all chains
- [ ] `OutputParserException` handled with fallback
- [ ] All 5 reflection questions answered (3–5 sentences each)

---

## Marking Scheme

| Part | Marks |
|------|-------|
| Part 1 — Pydantic model (fields + validators) | 10 |
| Part 2 — Chain 1: Sentiment + CoT | 10 |
| Part 2 — Chain 2: Features + Few-shot | 10 |
| Part 2 — Chain 3: Summary + Streaming | 10 |
| Part 2 — Chain 4: Urgency + SC + ToT | 10 |
| Part 3a — Batch pipeline + summary table | 15 |
| Part 3b — Cost tracking | 10 |
| Part 3c — Error handling | 5 |
| Part 4 — Reflection questions (5 x 4 marks) | 20 |
| **Total** | **100** |

---

## Grading Criteria

**Full marks:** Code runs cleanly. All session concepts are used correctly and intentionally. Reflection answers show understanding, not just definitions.

**Partial marks:** Code runs but uses wrong session concepts (e.g. zero-shot where few-shot was asked). Reflection answers are vague or copied from notes.

**Zero marks for a part:** Code doesn't run. Session concept completely missing.

---

## Setup

```bash
pip install langchain langchain-openai langchain-core pydantic python-dotenv
```

```
# .env file in same folder as your notebook
OPENAI_API_KEY=sk-...
```

---
