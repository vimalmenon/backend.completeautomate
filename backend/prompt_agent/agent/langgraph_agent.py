from collections.abc import Callable
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph


class LangGraphAgentState(TypedDict, total=False):
    context: dict[str, Any]
    error: str | None
    input: Any
    messages: list[dict[str, Any]]
    output: Any
    prompt: str | None
    status: str


class LangGraphAgent:
    def __init__(
        self,
        runner: Callable[[LangGraphAgentState], Any] | None = None,
    ) -> None:
        self.runner = runner or self.run
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(LangGraphAgentState)
        builder.add_node("initialize", self._initialize_state)
        builder.add_node("execute", self._execute)
        builder.add_edge(START, "initialize")
        builder.add_edge("initialize", "execute")
        builder.add_edge("execute", END)
        return builder.compile()

    def _initialize_state(self, state: LangGraphAgentState) -> LangGraphAgentState:
        return {
            "context": dict(state.get("context", {})),
            "error": state.get("error"),
            "input": state.get("input"),
            "messages": list(state.get("messages", [])),
            "output": state.get("output"),
            "prompt": state.get("prompt"),
            "status": state.get("status", "initialized"),
        }

    def _execute(self, state: LangGraphAgentState) -> LangGraphAgentState:
        try:
            result = self.runner(state)
        except Exception as error:
            return {
                "error": str(error),
                "output": None,
                "status": "failed",
            }

        if isinstance(result, dict):
            next_state = dict(result)
        else:
            next_state = {"output": result}

        next_state.setdefault("error", None)
        next_state.setdefault("status", "completed")
        return next_state

    def invoke(self, state: LangGraphAgentState) -> LangGraphAgentState:
        return self.graph.invoke(state)

    def run(self, state: LangGraphAgentState) -> Any:
        raise NotImplementedError("LangGraphAgent.run must be implemented")
