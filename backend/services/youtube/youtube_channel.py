class YouTubeChannel:

    def fetch_channel_details(self, channel_id: str):
        pass


# from googleapiclient.discovery import build

# class YouTubeChannel:
#     def __init__(self, api_key: str):
#         self.youtube = build('youtube', 'v3', developerKey=api_key)

#     def fetch_channel_details(self, channel_id: str):
#         request = self.youtube.channels().list(
#             part='snippet,statistics,contentDetails',
#             id=channel_id
#         )
#         response = request.execute()
#         return response['items'][0] if response['items'] else None
