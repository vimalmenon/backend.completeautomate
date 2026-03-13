from backend.data import YouTubeVideoJobData
from backend.enum.status import TaskStatusEnum
from backend.generator.base_generator import BaseGenerator

# YouTubeVideoStart = "YouTubeVideoStart"
# YouTubeVideoFixTranscript = "YouTubeVideoFixTranscript"
# YouTubeVideoMetadataSelection = "YouTubeVideoMetadataSelection"
# YouTubeVideoThumbnailSelection = "YouTubeVideoThumbnailSelection"
# YouTubeVideoComplete = "YouTubeVideoComplete"


class YouTubeVideoGenerator(BaseGenerator):

    def __init__(self, task):
        super().__init__(task)
        self.job_data = YouTubeVideoJobData.to_cls(self.task.payload)

    def generate(self) -> TaskStatusEnum:
        self.__create_video_db()
        self.__fix_transcript()
        self.__create_transcript_summary()
        self.__create_metadata_suggestions()
        self.__select_metadata_suggestion()
        self.__create_thumbnail_prompt_suggestions()
        self.__generate_thumbnails()
        self.__select_thumbnail()
        self.__review_video()
        self.__job_complete()
        return TaskStatusEnum.IN_PROGRESS

    def __create_video_db(self):
        pass

    def __fix_transcript(self):
        pass

    def __create_transcript_summary(self):
        pass

    def __create_metadata_suggestions(self):
        pass

    def __select_metadata_suggestion(self):
        pass

    def __create_thumbnail_prompt_suggestions(self):
        pass

    def __generate_thumbnails(self):
        pass

    def __select_thumbnail(self):
        pass

    def __review_video(self):
        pass

    def __job_complete(self):
        pass
