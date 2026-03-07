from faker import Faker

from backend.data import YouTubeChannelDBData

faker = Faker()


def youtube_channel_factory() -> YouTubeChannelDBData:
    return YouTubeChannelDBData(
        ref_id=faker.str(),
        title=faker.name(),
        description=faker.text(),
        custom_url=faker.url(),
        published_at=faker.date_time(),
        last_updated_at=faker.date_time(),
        country=faker.country(),
        thumbnail_url=faker.image_url(),
        banner_image_url=faker.image_url(),
        privacy_status=faker.word(),
        made_for_kids=faker.boolean(),
        task_id=faker.uuid4(),
        stats=[],
    )
