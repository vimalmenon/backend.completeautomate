from logging import getLogger
from typing import Any

from youtube_transcript_api import YouTubeTranscriptApi

from backend.exception.app_exception import AppException
from backend.integration.youtube.youtube_auth import YouTubeAuth
from backend.integration.youtube.youtube_studio_post import (
    create_community_post_via_studio,
)

logger = getLogger(__name__)


class YouTubeAPI:

    def __init__(self):
        self.auth = YouTubeAuth()

    def update_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        try:
            youtube = self.auth.get_authenticated_service()
            request = youtube.thumbnails().set(
                videoId=video_id, media_body=thumbnail_path
            )
            response = request.execute()
            logger.info(
                f"Thumbnail updated successfully for video ID: {video_id} {response}"
            )
            return True
        except Exception as e:
            logger.error(f"An error occurred updating thumbnail: {e}")
            raise AppException(f"An error occurred updating thumbnail: {str(e)}")

    def update_video_metadata(
        self,
        video_id: str,
        title: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
    ) -> bool:
        try:
            if not video_id or not video_id.strip():
                raise AppException("Video ID is required")

            if title is None and description is None and tags is None:
                raise AppException(
                    "At least one field must be provided: title, description, or tags"
                )

            youtube = self.auth.get_authenticated_service()
            video_response = (
                youtube.videos().list(part="snippet", id=video_id).execute()
            )
            if not video_response.get("items"):
                raise AppException(f"Video with ID '{video_id}' not found")

            current_snippet = video_response["items"][0].get("snippet", {})
            updated_snippet = {
                "categoryId": current_snippet.get("categoryId", "22"),
                "title": (
                    title if title is not None else current_snippet.get("title", "")
                ),
                "description": (
                    description
                    if description is not None
                    else current_snippet.get("description", "")
                ),
            }

            if tags is not None:
                updated_snippet["tags"] = tags
            elif "tags" in current_snippet:
                updated_snippet["tags"] = current_snippet["tags"]
            update_response = (
                youtube.videos()
                .update(
                    part="snippet",
                    body={
                        "id": video_id,
                        "snippet": updated_snippet,
                    },
                )
                .execute()
            )

            logger.info(
                "Video metadata updated successfully for ID: %s (title=%s, description=%s, tags=%s)",
                video_id,
                title is not None,
                description is not None,
                tags is not None,
            )
            return bool(update_response)
        except Exception as e:
            logger.error("An error occurred while updating video metadata: %s", e)
            raise AppException(
                f"An error occurred while updating video metadata: {str(e)}"
            )

    def get_channel_info(self, channel_id: str) -> Any:
        """
        Get detailed information about a YouTube channel.

        Args:
            channel_id: The YouTube channel ID

        Returns:
            Dictionary containing channel information including:
            - id: Channel ID
            - title: Channel title
            - description: Channel description
            - customUrl: Custom URL (if available)
            - publishedAt: When the channel was created
            - thumbnails: Channel thumbnails
            - statistics: Subscriber count, view count, video count
            - status: Privacy status and other status info
            - brandingSettings: Banner image and other branding info
        """
        try:
            youtube = self.auth.get_authenticated_service()
            request = youtube.channels().list(
                part="snippet,statistics,status,brandingSettings",
                id=channel_id,
            )
            response = request.execute()

            if not response.get("items"):
                raise AppException(f"Channel with ID '{channel_id}' not found")

            channel_data = response["items"][0]
            logger.info(f"Channel info retrieved successfully for ID: {channel_id}")
            return channel_data

        except Exception as e:
            logger.error(f"An error occurred while fetching channel info: {e}")
            raise AppException(
                f"An error occurred while fetching channel info: {str(e)}"
            )

    def create_text_post(
        self, channel_id: str, text: str, video_id: str | None = None
    ) -> bool:
        """
        Create a YouTube channel Community text post.

        Args:
            channel_id: The YouTube channel ID
            text: The text content of the post
            video_id: Unused. Kept for backward compatibility.

        Returns:
            True if post was created successfully, False otherwise
        """
        try:
            if not channel_id or not channel_id.strip():
                raise AppException("Channel ID is required")
            if not text or not text.strip():
                raise AppException("Post text is required")

            if video_id:
                logger.warning(
                    "video_id is ignored for create_text_post because Community posts are channel-level"
                )

            return create_community_post_via_studio(channel_id=channel_id, text=text)

        except Exception as e:
            logger.error(f"An error occurred while creating post: {e}")
            raise AppException(f"An error occurred while creating post: {str(e)}")

    def create_video_comment(self, channel_id: str, video_id: str, text: str) -> bool:
        """
        Create a top-level comment on a specific video.

        Args:
            channel_id: The YouTube channel ID
            video_id: The target YouTube video ID
            text: The comment text

        Returns:
            True if comment was created successfully, False otherwise
        """
        try:
            if not channel_id or not channel_id.strip():
                raise AppException("Channel ID is required")
            if not video_id or not video_id.strip():
                raise AppException("Video ID is required")
            if not text or not text.strip():
                raise AppException("Comment text is required")

            youtube = self.auth.get_authenticated_service()

            body = {
                "snippet": {
                    "channelId": channel_id,
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": text,
                        }
                    },
                },
            }

            request = youtube.commentThreads().insert(
                part="snippet",
                body=body,
            )
            response = request.execute()

            if response:
                logger.info(
                    "Comment created successfully with ID: %s on video ID: %s",
                    response.get("id"),
                    video_id,
                )
                return True
            return False

        except Exception as e:
            logger.error(f"An error occurred while creating comment: {e}")
            raise AppException(f"An error occurred while creating comment: {str(e)}")

    def list_all_videos(self, channel_id: str, max_results: int = 50) -> list[dict]:
        """
        List all videos from a channel, including published, scheduled, and unlisted videos.

        Args:
            channel_id: The YouTube channel ID
            max_results: Maximum number of videos to retrieve per page (default: 50, max: 50)

        Returns:
            List of video dictionaries containing:
            - videoId: Video ID
            - title: Video title
            - description: Video description
            - publishedAt: When video was/will be published
            - thumbnails: Video thumbnails
            - status: Video privacy status (public, unlisted, private, scheduled)
            - statistics: View count, like count, comment count
        """
        try:
            youtube = self.auth.get_authenticated_service()

            # Get uploads playlist ID for this channel
            channel_request = youtube.channels().list(
                part="contentDetails", id=channel_id
            )
            channel_response = channel_request.execute()

            if not channel_response.get("items"):
                raise AppException(f"Channel with ID '{channel_id}' not found")

            uploads_playlist_id = channel_response["items"][0]["contentDetails"][
                "relatedPlaylists"
            ]["uploads"]

            # List all videos from the uploads playlist (includes published and scheduled)
            videos = []
            next_page_token = None

            while True:
                playlist_request = youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=uploads_playlist_id,
                    maxResults=max_results,
                    pageToken=next_page_token,
                )
                playlist_response = playlist_request.execute()

                # Get detailed video information including status
                for item in playlist_response.get("items", []):
                    video_id = item["contentDetails"]["videoId"]
                    video_request = youtube.videos().list(
                        part="snippet,statistics,status",
                        id=video_id,
                    )
                    video_response = video_request.execute()

                    if video_response.get("items"):
                        videos.append(video_response["items"][0])

                next_page_token = playlist_response.get("nextPageToken")
                if not next_page_token:
                    break

            logger.info(f"Retrieved {len(videos)} videos from channel ID: {channel_id}")
            return videos

        except Exception as e:
            logger.error(f"An error occurred while fetching videos: {e}")
            raise AppException(f"An error occurred while fetching videos: {str(e)}")

    def fetch_video_details(self, video_id: str) -> Any:
        """
        Fetch detailed information about a specific video.

        Args:
            video_id: The YouTube video ID

        Returns:
            Dictionary containing video information including:
            - id: Video ID
            - title: Video title
            - description: Video description
            - publishedAt: When video was/will be published
            - thumbnails: Video thumbnails
            - status: Video privacy status (public, unlisted, private, scheduled)
            - statistics: View count, like count, comment count
        """
        try:
            youtube = self.auth.get_authenticated_service()
            request = youtube.videos().list(
                part="snippet,statistics,status",
                id=video_id,
            )
            response = request.execute()

            if not response.get("items"):
                raise AppException(f"Video with ID '{video_id}' not found")

            video_data = response["items"][0]
            logger.info(f"Video details retrieved successfully for ID: {video_id}")
            return video_data

        except Exception as e:
            logger.error(f"An error occurred while fetching video details: {e}")
            raise AppException(
                f"An error occurred while fetching video details: {str(e)}"
            )

    def get_transcript(
        self,
        video_id: str,
    ) -> Any:
        """
        Get transcript for a YouTube video.

        Args:
            video_id: YouTube video ID
        Returns:
            List of transcript entries with 'text', 'start', 'duration' keys
        """
        try:
            return YouTubeTranscriptApi().fetch(video_id)
        except Exception as e:
            logger.error(f"An error occurred while fetching transcript: {e}")
            raise AppException(f"An error occurred while fetching transcript: {str(e)}")
