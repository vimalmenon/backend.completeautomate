from uuid import UUID

from backend.data import YouTubeChannelDBData, YouTubeVideoDBData
from backend.factory.common import fake_date, faker


def youtube_channel_factory(**kwargs) -> YouTubeChannelDBData:
    return YouTubeChannelDBData(
        ref_id=kwargs.get("ref_id") or faker.str(),
        title=faker.name(),
        description=faker.text(),
        custom_url=faker.url(),
        published_at=faker.date_time(),
        last_updated_at=fake_date(),
        country=faker.country(),
        thumbnail_url=faker.image_url(),
        banner_image_url=faker.image_url(),
        privacy_status=faker.word(),
        made_for_kids=faker.boolean(),
        task_id=UUID(faker.uuid4()),
        stats=[],
    )


def youtube_video_factory(**kwargs) -> YouTubeVideoDBData:
    return YouTubeVideoDBData(
        ref_id=kwargs.get("ref_id") or faker.str(),
        published_at=faker.date_time(),
        last_updated_at=faker.date_time(),
        title=faker.text(),
        description=faker.name(),
        thumbnail=faker.text(),
        tags=[],
        language=faker.name(),
        task_id=UUID(faker.uuid4()),
        stats=[],
    )
