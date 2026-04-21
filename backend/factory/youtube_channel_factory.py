from backend.data import YouTubeChannelDBData
from backend.factory.common import fake_date, fake_url, faker


def youtube_channel_factory(**kwargs) -> YouTubeChannelDBData:
    return YouTubeChannelDBData(
        ref_id=kwargs.get("ref_id") or faker.str(),
        title=faker.name(),
        description=faker.text(),
        custom_url=fake_url(),
        published_at=fake_date(),
        last_updated_at=fake_date(),
        country=faker.country(),
        thumbnail_url=faker.image_url(),
        banner_image_url=faker.image_url(),
        privacy_status=faker.word(),
        made_for_kids=faker.boolean(),
        stats=[],
        channel_id=faker.text(),
    )
