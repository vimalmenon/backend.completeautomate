"""LangGraph DynamoDB persistence helpers.

Reuses the existing AWS session and handles offline mode automatically.
"""

from backend.config.env import env
from backend.config.session import AWSSession
from langgraph.checkpoint.dynamodb import DynamoDBSaver
from langgraph.store.dynamodb import DynamoDBStore

CHECKPOINT_TABLE = "CA#LANGGRAPH_CHECKPOINT"
STORE_TABLE = "CA#LANGGRAPH_STORE"


def get_checkpointer() -> DynamoDBSaver:
    """Create a DynamoDB checkpointer for LangGraph state persistence."""
    session = AWSSession.get_static_session()
    client = session.client("dynamodb", region_name=env.AWS_REGION)
    return DynamoDBSaver(
        client=client,
        table_name=CHECKPOINT_TABLE,
    )


def get_store() -> DynamoDBStore:
    """Create a DynamoDB store for LangGraph long-term memory."""
    session = AWSSession.get_static_session()
    client = session.client("dynamodb", region_name=env.AWS_REGION)
    return DynamoDBStore(
        client=client,
        table_name=STORE_TABLE,
    )
