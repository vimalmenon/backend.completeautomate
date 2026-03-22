from enum import Enum
from random import choice
from typing import Type, TypeVar
from uuid import UUID

from faker import Faker

faker = Faker()

T = TypeVar("T", bound=Enum)


def seed_faker(seed: int = 42) -> None:
    faker.seed_instance(seed)


def fake_date():
    return faker.date_time()


def fake_uuid() -> UUID:
    return UUID(faker.uuid4())


def fake_url() -> str:
    return faker.url()


def fake_image_url() -> str:
    """Generate a fake image URL."""
    return faker.image_url()


def fake_text() -> str:
    """Generate fake text."""
    return faker.text()


def fake_name() -> str:
    """Generate a fake name."""
    return faker.name()


def fake_word() -> str:
    """Generate a fake word."""
    return faker.word()


def fake_country() -> str:
    """Generate a fake country name."""
    return faker.country()


def fake_boolean() -> bool:
    """Generate a fake boolean value."""
    return faker.boolean()


def fake_str() -> str:
    """Generate a fake string."""
    return str(faker.pystr())


def pick_random_enum(enum_class: Type[T]) -> T:
    """Pick a random value from an enum class.

    Args:
        enum_class: The enum class to pick from.

    Returns:
        A random enum value.
    """
    return choice(list(enum_class))


def fake_filename(extension: str = "txt") -> str:
    """Generate a fake file name with the given extension (default: txt)."""
    return faker.file_name(extension=extension)
