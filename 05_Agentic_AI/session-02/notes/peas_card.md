
```
┌──────────────────────────────────────────────────────────┐
│                  CODESENTINEL PEAS                       │
├──────────────────────────────────────────────────────────┤
│ PERFORMANCE                                              │
│  • Bug detection rate > 90%                             │
│  • False positive rate < 10%                            │
│  • Latency < 60 sec                                     │
│  • Token cost < $0.05/review                            │
│  • Developer acceptance > 75%                           │
├──────────────────────────────────────────────────────────┤
│ ENVIRONMENT                                              │
│  • GitHub repos — Python, JS codebases                  │
│  • Partially Observable (diff only, not full codebase)  │
│  • Stochastic (LLM non-deterministic)                   │
│  • Sequential (author history matters)                   │
│  • Static during review, Discrete actions               │
│  • Currently Single-agent → Multi-agent roadmap         │
├──────────────────────────────────────────────────────────┤
│ ACTUATORS                                                │
│  • post_pr_comment (HITL currently)                     │
│  • request_changes (future)                             │
│  • approve_pr (HITL always)                             │
│  • notify_author (future, auto)                         │
├──────────────────────────────────────────────────────────┤
│ SENSORS                                                  │
│  • get_pr_details, get_pr_files, get_file_content       │
│  • BLIND TO: full codebase, CI results, author history  │
└──────────────────────────────────────────────────────────┘
```