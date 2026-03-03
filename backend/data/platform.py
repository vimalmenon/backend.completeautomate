from dataclasses import dataclass

from backend.enum import PlatformEnum


@dataclass
class PlatformDBData:
    platform_type: PlatformEnum
    data: dict

    def to_json(self) -> dict:
        return {"data": self.data, "platform_type": self.platform_type.value}

    @classmethod
    def to_cls(cls, data):
        return cls(data=data["data"], platform_type=PlatformEnum(data["platform_type"]))
