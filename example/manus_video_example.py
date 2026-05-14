import os
from pathlib import Path

from backend.ai import ManusVideoGenerator


OUTPUT_PATH = Path("example/output/manus_video_example.mp4")
PROMPT = """
Create a short presenter-style avatar clip for Complete Automate.

The avatar should introduce an automation workflow, gesture naturally, and keep
the pacing suitable for a short product teaser.
""".strip()


def _get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


class ExampleManusClient:
    def generate_video(
        self,
        *,
        prompt: str,
        model: str,
        output_format: str,
    ) -> dict[str, bytes]:
        payload = (
            f"Scaffolded Manus output\nmodel={model}\nformat={output_format}\n"
            f"prompt={prompt}\n"
        ).encode("utf-8")
        return {"video_bytes": payload}


def main() -> None:
    api_key = _get_required_env("MANUS_API_KEY")
    generator = ManusVideoGenerator(api_key=api_key, client=ExampleManusClient())
    saved_path = generator.save_video(prompt=PROMPT, output_path=OUTPUT_PATH)

    print(f"Saved scaffold video artifact to: {saved_path}")
    print("Replace ExampleManusClient with the live Manus adapter when API details are available.")


if __name__ == "__main__":
    main()