from backend.data import ImageGeneratorJobData, S3Data, TaskData
from backend.database.image.image_generator_db import ImageGeneratorDB
from backend.enum.status import TaskStatusEnum
from backend.generator.base_generator import BaseGenerator
from backend.integration.image_generation.image_model import ImageModel
from backend.integration.storage.s3_storage import S3Storage


class ImageGenerator(BaseGenerator):
    def __init__(self, task: TaskData):
        super().__init__(task)
        payload = task.payload
        s3_data = S3Data(
            name=payload["name"],
            content_type=S3Data.detect_content_type_from_name(payload["name"]),
        )
        self.job_data = ImageGeneratorJobData.to_cls(
            {**task.payload, "data": s3_data.to_json(), "task_id": task.id}
        )

    def generate(self) -> TaskStatusEnum:
        image = ImageModel().generate(self.job_data.prompt)
        S3Storage().upload_data(self.job_data.data, image)
        ImageGeneratorDB().save_to_db(self.job_data)
        return TaskStatusEnum.REVIEW
