from enum import Enum


class ActionEnum(str, Enum):
    restore_from_s3 = "restore_from_s3"
    restore_from_local = "restore_from_local"
    download_to_local = "download_to_local"
    transform = "transform"
    show_jobs = "show_jobs"
