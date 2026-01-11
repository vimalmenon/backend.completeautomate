from dataclasses import dataclass


@dataclass
class Message:
    role: str
    content: str
    assigned_to: str
    tool_call_name: str | None = None
    tool_call_results: str | None = None
    tool_call_id: str | None = None

    def to_dict(self) -> dict:
        return {
            "role": self.role, 
            "content": self.content, 
            "assigned_to": self.assigned_to,
            "tool_call_name": self.tool_call_name,
            "tool_call_results": self.tool_call_results,
            "tool_call_id": self.tool_call_id,
        }