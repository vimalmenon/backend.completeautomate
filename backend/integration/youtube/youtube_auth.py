import os
import pickle
from logging import getLogger

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
logger = getLogger(__name__)


class YouTubeAuth:
    creds = None

    def __init__(self):
        self.creds = None
        if os.path.exists("backend/output/pickle/token.pickle"):
            with open("backend/output/pickle/token.pickle", "rb") as token:
                self.creds = pickle.load(token)

    def get_authenticated_service(self):
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                # Refresh the token if it's expired [citation:2][citation:8]
                self.creds.refresh(Request())
                logger.info("Access token refreshed successfully")
            else:
                # Run the OAuth flow to get new credentials [citation:6][citation:8]
                flow = InstalledAppFlow.from_client_secrets_file(
                    "backend/output/json/client_secret.json", SCOPES
                )
                self.creds = flow.run_local_server(port=0)
                logger.info("New access token obtained")

            # Save the credentials for the next run [citation:2][citation:6]
            with open("backend/output/pickle/token.pickle", "wb") as token:
                pickle.dump(self.creds, token)
                logger.info("Credentials saved to token.pickle")

        logger.debug("Token expires at: %s", self.creds.expiry)
        logger.debug(
            "Refresh token available: %s",
            "Yes" if self.creds.refresh_token else "No",
        )

        # Build and return the YouTube service object [citation:2][citation:8]
        return build("youtube", "v3", credentials=self.creds)
