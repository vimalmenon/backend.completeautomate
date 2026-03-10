from uuid import UUID

from faker import Faker

faker = Faker()


def fake_date():
    return faker.date_time()


def fake_uuid() -> UUID:
    return UUID(faker.uuid4())


def fake_url() -> str:
    return faker.url()
