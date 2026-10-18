from langfuse import propagate_attributes

async def run_agent_with_trace(*, langfuse, agent, conversation_id, messages):
    with langfuse.start_as_current_observation(
        name="healthlink-agent-run",
        as_type="agent",
        input={"message_count": len(messages)},
    ) as observation:
        with propagate_attributes(
            session_id=conversation_id,
            tags=["healthlink", "development"],
        ):
            try:
                result = await agent.ainvoke(
                    {
                        "messages": messages,
                        "tool_calls": [],
                        "model_calls": 0,
                        "reply": "",
                        "booking_proposal": None,
                    },
                    config={"recursion_limit": 12},
                )
                observation.update(output={
                    "reply_characters": len(result["reply"]),
                    "model_calls": result["model_calls"],
                    "booking_proposal_created": result.get("booking_proposal") is not None,
                })
                return result
            except Exception as exc:
                observation.update(
                    level="ERROR",
                    status_message=type(exc).__name__,
                    output={"error_type": type(exc).__name__},
                )
                raise

