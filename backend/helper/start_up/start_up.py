from backend.data.s3 import S3Data
from backend.helper.folder_helper.folder_helper import FolderHelper
from backend.integration.storage.s3_storage import S3Storage


class StartUp:

    def __init__(self):
        for path in ["pickle/token.pickle", "json/client_secret.json"]:
            data = S3Data.to_cls_from_path(path)
            if not FolderHelper().check_if_file_exists(data.downloaded_path):
                S3Storage().download_data(data)
