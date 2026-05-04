from unittest.mock import MagicMock

import pytest

from backend.ai.video_generation.manus_video_generator import ManusVideoGenerator
from backend.exception import AppException


@pytest.mark.unit
class TestManusVideoGenerator:
    def test_generate_video_returns_bytes_response(self) -> None:
        client = MagicMock()
        client.generate_video.return_value = b"video-bytes"

        generator = ManusVideoGenerator(api_key="manus-key", client=client)

        result = generator.generate_video("avatar prompt")

        assert result == b"video-bytes"
        client.generate_video.assert_called_once_with(
            prompt="avatar prompt",
            model="manus-avatar-v1",
            output_format="mp4",
        )

    def test_generate_video_returns_dict_payload_bytes(self) -> None:
        client = MagicMock()
        client.generate_video.return_value = {"video_bytes": b"video-bytes"}

        generator = ManusVideoGenerator(api_key="manus-key", client=client)

        assert generator.generate_video("avatar prompt") == b"video-bytes"

    def test_generate_video_raises_for_blank_prompt(self) -> None:
        generator = ManusVideoGenerator(api_key="manus-key", client=MagicMock())

        with pytest.raises(AppException, match="Prompt is required"):
            generator.generate_video("   ")

    def test_generate_video_raises_when_api_key_missing(self) -> None:
        generator = ManusVideoGenerator(api_key=None, client=MagicMock())

        with pytest.raises(AppException, match="Manus API key is required"):
            generator.generate_video("avatar prompt")

    def test_generate_video_raises_when_client_missing(self) -> None:
        generator = ManusVideoGenerator(api_key="manus-key", client=None)

        with pytest.raises(AppException, match="Manus client is not configured"):
            generator.generate_video("avatar prompt")

    def test_generate_video_raises_when_client_errors(self) -> None:
        client = MagicMock()
        client.generate_video.side_effect = RuntimeError("bad request")

        generator = ManusVideoGenerator(api_key="manus-key", client=client)

        with pytest.raises(AppException, match="Manus video generation error"):
            generator.generate_video("avatar prompt")

    def test_save_video_persists_generated_video(self, tmp_path) -> None:
        client = MagicMock()
        client.generate_video.return_value = {"content": b"video-bytes"}
        target = tmp_path / "video.mp4"

        generator = ManusVideoGenerator(api_key="manus-key", client=client)
        saved_path = generator.save_video("avatar prompt", target)

        assert saved_path == target
        assert target.read_bytes() == b"video-bytes"

    def test_generate_video_raises_for_unexpected_response(self) -> None:
        client = MagicMock()
        client.generate_video.return_value = {"unexpected": b"value"}

        generator = ManusVideoGenerator(api_key="manus-key", client=client)

        with pytest.raises(AppException, match="No video data found"):
            generator.generate_video("avatar prompt")