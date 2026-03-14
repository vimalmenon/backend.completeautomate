from backend.data import ImageGeneratorJobData, S3Data, TaskData
from backend.database.image.image_generator_db import ImageGeneratorDB
from backend.enum import TaskStatusEnum
from backend.generator.base_generator import BaseGenerator
from backend.integration.image_generation.open_router_image_generation import (
    ImageModelList,
    OpenRouterImageGeneration,
)
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
        # Use specified model or default to FLUX
        model = ImageModelList.FLUX  # Default
        if self.job_data.model:
            try:
                model = ImageModelList[self.job_data.model.upper()]
            except KeyError:
                # If invalid model specified, fall back to default
                pass

        image = OpenRouterImageGeneration(model=model).generate(self.job_data.prompt)
        S3Storage().upload_data(self.job_data.data, image)
        ImageGeneratorDB().save_to_db(self.job_data)
        return TaskStatusEnum.REVIEW
