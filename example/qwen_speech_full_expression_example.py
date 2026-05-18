from pathlib import Path

OUTPUT_PATH = Path("example/output/qwen_speech_full_expression_2_minutes.mp3")
WORDS_PER_MINUTE = 145
SPEECH_RATE = 0.92
INSTRUCTIONS = (
    "Narrate like a premium documentary voiceover with emotional range. "
    "Start calm and inviting, build energy through the middle, and land with "
    "confidence and warmth. Use clear articulation, natural pauses, vivid "
    "intonation, and expressive emphasis on key phrases without sounding theatrical."
)

SCRIPT = """
Take a breath, settle in, and picture this for a moment.

You wake up tomorrow with a system that quietly handles the repetitive work that has been stealing your time for months. Emails are sorted. Routine updates are written. Reports are drafted before your first coffee. Your content pipeline is moving, your notes are organized, and the next best action is already waiting for you.

That is the real promise of automation. It is not cold. It is not robotic. It is not about replacing judgment. It is about protecting your focus so your best thinking can finally go where it belongs.

Now imagine what changes when the noise drops.

You respond with more clarity. You create with more energy. You make decisions faster because the clutter is gone. And instead of constantly reacting, you begin to design your day with intention.

This is where momentum starts. One workflow becomes two. Two become ten. Soon, the tasks that once felt heavy become background operations, running reliably, calmly, almost invisibly.

And here is the part people miss: the emotional effect is real. Relief. Confidence. Even a little excitement. Because when systems support you properly, work feels lighter, sharper, and far more human.

So if you have been waiting for a sign to simplify, this is it.

Start with one process. Make it clean. Make it repeatable. Then let automation carry the weight while you carry the vision.

The future is not about doing more things at once. It is about doing the right things with more presence, more control, and a lot more expression.
""".strip()


def estimate_duration_seconds(text: str, rate: float) -> float:
    word_count = len(text.split())
    effective_wpm = WORDS_PER_MINUTE * rate
    return (word_count / effective_wpm) * 60


def main() -> None:
    from backend.ai.speech_generation import QwenSpeechGenerator

    estimated_duration = estimate_duration_seconds(SCRIPT, SPEECH_RATE)
    if not 110 <= estimated_duration <= 130:
        raise ValueError(
            f"Script duration is {estimated_duration:.1f}s, expected about 120s"
        )

    generator = QwenSpeechGenerator(
        rate=SPEECH_RATE,
        pitch=1.08,
        volume=70,
        instructions=INSTRUCTIONS,
    )
    saved_path = generator.save_speech(text=SCRIPT, output_path=OUTPUT_PATH)

    print(f"Saved audio to: {saved_path}")
    print(f"Estimated duration: {estimated_duration:.1f} seconds")


if __name__ == "__main__":
    main()
