import os
from pathlib import Path

from backend.ai.speech_generation import ResembleSpeechGenerator


OUTPUT_PATH = Path("example/output/resemble_speech_example.wav")
SCRIPT = """
Automation is at its best when it gives your time back.

This short example uses the Resemble API to turn plain text into speech,
save the result locally, and keep the workflow simple enough to reuse in larger
content pipelines.

Once your API key, project UUID, and voice UUID are configured, you can swap
this script for your own narration and generate production-ready audio in a
single step.
""".strip()


def _get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def main() -> None:
    project_uuid = _get_required_env("RESEMBLE_PROJECT_UUID")
    voice_uuid = os.environ.get("RESEMBLE_VOICE_UUID") or _get_required_env(
        "RESEMBLE_TTS_ID"
    )

    generator = ResembleSpeechGenerator(
        project_uuid=project_uuid,
        voice_uuid=voice_uuid,
        output_format="wav",
        sample_rate=48000,
        precision="PCM_16",
        title="Resemble Speech Example",
    )
    saved_path = generator.save_speech(text=SCRIPT, output_path=OUTPUT_PATH)

    print(f"Saved audio to: {saved_path}")


if __name__ == "__main__":
    main()