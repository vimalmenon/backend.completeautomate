from enum import Enum


class ActionEnum(str, Enum):
    transform = "transform"
    backup_up_db = "backup_up_db"
    restore_db = "restore_db"
    restore_from_local = "restore_from_local"
    download_to_local = "download_to_local"
