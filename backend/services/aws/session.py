import boto3

from backend.config.env import env


class Session:
    def get_session(self):
        return boto3.Session(
            aws_access_key_id=env.AWS_CLIENT_ID,
            aws_secret_access_key=env.AWS_SECRET,
            region_name=env.AWS_REGION,
        )
