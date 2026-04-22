import pytest

from backend.prompt_agent.agent.langgraph_agent import LangGraphAgent


def test_langgraph_agent_initializes_and_invokes_runner() -> None:
    agent = LangGraphAgent(
        runner=lambda state: {
            "context": {**state["context"], "step": "ran"},
            "output": f"processed:{state['input']}",
        }
    )

    result = agent.invoke({"input": "hello"})

    assert result["input"] == "hello"
    assert result["context"] == {"step": "ran"}
    assert result["messages"] == []
    assert result["output"] == "processed:hello"
    assert result["status"] == "completed"
    assert result["error"] is None


def test_langgraph_agent_preserves_existing_state_defaults() -> None:
    agent = LangGraphAgent(runner=lambda state: {"output": state["input"]})

    result = agent.invoke(
        {
            "context": {"source": "test"},
            "input": "hello",
            "messages": [{"role": "user", "content": "hello"}],
            "prompt": "Say hello",
        }
    )

    assert result["context"] == {"source": "test"}
    assert result["messages"] == [{"role": "user", "content": "hello"}]
    assert result["prompt"] == "Say hello"
    assert result["output"] == "hello"
    assert result["status"] == "completed"


def test_langgraph_agent_returns_failed_state_on_runner_error() -> None:
    def failing_runner(_: dict) -> str:
        raise RuntimeError("graph failed")

    agent = LangGraphAgent(runner=failing_runner)

    result = agent.invoke({"input": "hello"})

    assert result["status"] == "failed"
    assert result["output"] is None
    assert result["error"] == "graph failed"


def test_langgraph_agent_requires_run_implementation_without_runner() -> None:
    agent = LangGraphAgent()

    with pytest.raises(NotImplementedError, match="must be implemented"):
        agent.invoke({"input": "hello"})
