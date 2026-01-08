from dataclasses import dataclass

from backend.enum import ImageTypeEnum, JobEnum


@dataclass
class GraphicDesignerClsData:
    image_type: ImageTypeEnum


@dataclass
class SocialMediaManagerData:
    job_type: JobEnum
