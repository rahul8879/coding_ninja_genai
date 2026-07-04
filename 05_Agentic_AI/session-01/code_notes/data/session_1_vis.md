# Session 1 — Flow Tracker
**Agentic AI | Coding Ninjas**

---

## FLOW

### 1. Hook (10 min)
- Story: 50 PRs/week, same bugs, no memory → "kya hoga agar ek smart reviewer hota?"
- Introduce **CodeSentinel** — yahi banenge Session 12 tak

### 2. Core Concepts (20 min)
- LLM ≠ Agent (calculator vs accountant)
- 4 Pillars: Perception → Memory → Planning → Tools
- Quick mention: frameworks exist to build this — LangChain, **LangGraph**, LlamaIndex
  - _"In detail Session 2 mein — aaj sirf naam jaano"_

### 3. Notebook — Three Generations (75 min)
- **Ex 1** — `RuleBasedCodeChecker` → false positive demo → rules fail at context
- **Ex 2** — `LLMCodeReviewer` (GPT-4o-mini) → understands context, no memory, no action
- **Ex 3** — `AgenticCodeSentinel` → goals + memory + tools → PR#1 then PR#2 (cross-PR memory live)
- **Ex 4** — Spectrum table (Rule-Based / LLM / Agentic) side by side

### 4. Roadmap Reveal (10 min)
- Session 12 architecture dikhao — FastAPI + LangGraph + ChromaDB + GitHub API
- 12-session journey map on screen

---

## LOGICAL ENDING 🎯

> _"Humne aaj haath se ek mini agent banaya — goals, memory, tools sab tha. But yeh sab manually wired tha. Real production agents mein hum yeh orchestration ek framework se karte hain._
>
> _Woh framework hai **LangGraph** — aur Session 2 mein hum isko zero se samjhenge aur CodeSentinel ka pehla real version usi pe banayenge."_

**Seed the problem:**
> _"Ek issue notice kiya? Agar main yeh agent dobara chalata hoon same PR pe — woh phir se comment karega. Duplicate. Memory thi, but proper state management nahi tha. Session 2 mein yahi fix karenge LangGraph ke saath."_

---

## SESSION 2 PREVIEW (tell students)
- LangGraph kya hai — State, Nodes, Edges, Graph
- CodeSentinel ka first real agent — GitHub PR live fetch + LLM review + comment post
- Memory problem ka solution start hoga

---

## QUICK RISK NOTES
- API key fail → pre-run output ready rakho
- Ex 3 mein zyada time lage → Ex 4 skip karo, roadmap mat chhodo
- Q&A first session mein long hoga — 10 min extra expect karo