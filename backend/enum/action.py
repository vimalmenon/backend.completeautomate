from enum import Enum


class ActionEnum(str, Enum):
    transform = "transform"
    restore_db = "restore_db"
    restore_from_local = "restore_from_local"
    download_to_local = "download_to_local"
    show_jobs = "show_jobs"
