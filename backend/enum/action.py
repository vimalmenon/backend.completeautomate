from enum import Enum


class ActionEnum(str, Enum):
    transform = "transform"
    download_from_s3 = "download_to_s3"
    backup_up_db = "backup_up_db"
    restore_db = "restore_db"
