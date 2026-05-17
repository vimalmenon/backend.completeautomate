"""LangGraph DynamoDB persistence helpers.

Reuses the existing AWS session and handles offline mode automatically.
"""
from backend.config.env import env
from backend.config.session import AWSSession

CHECKPOINT_TABLE = "CA#LANGGRAPH_CHECKPOINT"


def get_checkpointer():
    """Create a DynamoDB checkpointer for LangGraph state persistence.

    Returns a DynamoDBSaver configured with the project's existing AWS session.

    Usage:
        from backend.config.langgraph_session import get_checkpointer
        graph = builder.compile(checkpointer=get_checkpointer())
    """
    from langgraph.checkpoint.dynamodb import DynamoDBSaver

    session = AWSSession.get_static_session()
    client = session.client("dynamodb", region_name=env.AWS_REGION)
    return DynamoDBSaver(
        client=client,
        table_name=CHECKPOINT_TABLE,
    )
