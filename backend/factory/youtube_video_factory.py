from uuid import UUID

from backend.data import YouTubeVideoDBData
from backend.factory.common import fake_date, faker


def youtube_video_factory(**kwargs) -> YouTubeVideoDBData:
    return YouTubeVideoDBData(
        ref_id=kwargs.get("ref_id") or faker.str(),
        published_at=fake_date(),
        last_updated_at=fake_date(),
        title=faker.text(),
        description=faker.name(),
        thumbnail=faker.text(),
        tags=[],
        language=faker.name(),
        task_id=kwargs.get("task_id") or UUID(faker.uuid4()),
        stats=[],
    )
