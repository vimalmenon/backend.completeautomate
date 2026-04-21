from backend.data import YouTubeVideoDBData
from backend.enum import YouTubeVideoTaskEnum
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
        task_status=YouTubeVideoTaskEnum.YouTubeVideoStart,
        language=faker.name(),
        stats=[],
        channel_id=faker.text(),
        video_id=faker.text(),
    )
