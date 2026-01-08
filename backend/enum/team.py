from enum import Enum
from typing import Self


class TeamEnum(str, Enum):
    _role: str
    _display_name: str

    OWNER = ("Owner", "Vimal Menon")
    RESEARCHER = ("Researcher", "Christopher Morris")
    SOCIAL_MEDIA_MANAGER = ("Social Media Manager", "Samantha Rogers")
    MANAGER = ("Manager", "Elara Turner")
    GRAPHIC_DESIGNER = ("Graphic Designer", "Iris Cooper")
    CONTENT_WRITER = ("Content Writer", "Sam Morris")

    def __new__(cls, role: str, name: str):
        obj = str.__new__(cls, role)
        obj._value_ = role
        obj._role = role
        obj._display_name = name
        return obj

    @property
    def role(self) -> str:
        return self._role

    @property
    def display_name(self) -> str:
        return self._display_name

    @staticmethod
    def __normalize(value: str) -> str:
        return value.strip().lower().replace(" ", "_").replace("-", "_")

    @classmethod
    def from_value(cls, value: str) -> Self:
        if value.strip() in cls.__members__:
            raise ValueError(f"{value} is not a valid TeamEnum")

        normalized = cls.__normalize(value)
        for member in cls:
            if (
                member.role == value
                or member.value == value
                or cls.__normalize(member.role) == normalized
                or cls.__normalize(member.value) == normalized
            ):
                return member
        raise ValueError(f"{value} is not a valid TeamEnum")
