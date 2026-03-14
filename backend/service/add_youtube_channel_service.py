from backend.manager import PlatformManager


class AddYouTubeChannelServices:

    def add_channel(self, channel_id: str) -> None:
        if ref_id := PlatformManager().get_platform_by_channel_id(channel_id):
            print(ref_id)
