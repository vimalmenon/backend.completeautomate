from faker import Faker

from backend.data import YouTubeJobData

faker = Faker()


def create_youtube_channel_job_factory(**kwargs) -> YouTubeJobData:
    return YouTubeJobData(ref_id=kwargs.get("ref_id") or faker.str())
