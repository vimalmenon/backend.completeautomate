from backend.data import YouTubeJobData
from backend.factory.common import faker


def create_youtube_channel_job_factory(**kwargs) -> YouTubeJobData:
    return YouTubeJobData(ref_id=kwargs.get("ref_id") or faker.str())
