from app.observability.client import create_observability_client
def main():
    client = create_observability_client()
    try:
        if not client.auth_check():
            raise RuntimeError("Langfuse authentication failed.")
        print("Langfuse authentication successful.")
        with client.start_as_current_observation(
            name="healthlink-connection-check",
            as_type="span",
            input={"check": "synthetic connection test"},
        ) as observation:
            observation.update(output={"status": "completed"})
        client.flush()
        print("Trace export attempted. Confirm it in the Langfuse dashboard.")
    finally:
        client.shutdown()


if __name__ == "__main__":
    main()
