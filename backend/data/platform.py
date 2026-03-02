from dataclasses import dataclass

from backend.enum import SocialMediaEnum


@dataclass
class Platform:
    platform_type: SocialMediaEnum
    data: dict
