from dataclasses import dataclass


@dataclass
class Message:
    role: str
    content: str
    assigned_to: str

    def to_dict(self) -> dict:
        return {
            "role": self.role, 
            "content": self.content, 
            "assigned_to": self.assigned_to
        }