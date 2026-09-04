"""Jarvis-lite command-line orchestrator.

Use --text for a hardware-free smoke test. Voice recording and wake-word
adapters can be added without changing intent parsing or skill routing.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from config import load_config
from code_agent import CodeAgent
from database import InteractionDatabase
from intent_parser import IntentParser
from router import run_intent
from stt import SpeechToText
from tts import speak


def response_emotion(action: str, result: str) -> str:
    if action in {"take_picture", "take_screenshot", "open_video", "open_app"} and not result.startswith(("I could", "I do not", "The command")):
        return "happy"
    if result.startswith(("I could", "I do not", "The command", "I found no")):
        return "empathetic"
    if action == "code_change":
        return "calm"
    return "calm"


def get_database_url() -> str:
    import os

    return "postgresql://{user}:{password}@{host}:{port}/{name}".format(
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        name=os.environ["DB_NAME"],
    )


def handle_command(command: str, config: dict, input_audio_path: Path | None = None) -> str:
    llm_config = config["llm"]
    intent = IntentParser(
        model=llm_config["model"],
        api_key_env=llm_config["api_key_env"],
    ).parse(command)
    if intent.action == "unknown":
        intent = intent.__class__("search_web", {"query": command})
    if intent.action == "code_change":
        return handle_code_change(command, config)
    parameters = {
        **intent.parameters,
        "videos": config["media"].get("videos", {}),
        "apps": config.get("apps", {}),
        "pictures_dir": config["media"].get("pictures_dir", "pictures"),
        "documents_dir": config.get("documents_dir", "documents"),
    }
    result = run_intent(intent.__class__(intent.action, parameters))
    voice_config = config["voice"]
    emotion = response_emotion(intent.action, result)
    audio_config = config.get("audio", {})
    output_audio_path = Path(audio_config.get("output_dir", "audio/output")) / f"response-{datetime.now():%Y%m%d-%H%M%S-%f}.wav"
    print(f"Jarvis: {result}")
    print("Preparing voice response...")
    try:
        saved_output_path = speak(
            result,
            voice_config.get("tts_enabled", False),
            voice_config.get("tts_voice", "David"),
            voice_config.get("tts_rate", 155),
            voice_config.get("tts_volume", 1.0),
            emotion,
            output_audio_path,
        )
    except Exception as error:
        print(f"Voice output unavailable: {error}")
        saved_output_path = None
    try:
        InteractionDatabase(get_database_url()).record(
            command,
            result,
            intent.action,
            emotion,
            str(input_audio_path) if input_audio_path else None,
            str(saved_output_path) if saved_output_path else None,
        )
    except Exception as error:
        print(f"Database logging unavailable: {error}")
    return result


def handle_code_change(command: str, config: dict) -> str:
    try:
        proposal = CodeAgent(model=config.get("coding", {}).get("model", "qwen2.5-coder:7b")).propose(command)
    except Exception as error:
        return f"I could not prepare that code change. Is Ollama running with the coding model installed? Details: {error}"
    edited_files = ", ".join(edit["path"] for edit in proposal["edits"])
    print(f"Proposed change: {proposal.get('summary', 'No summary provided.')}")
    print(f"Files: {edited_files}")
    try:
        confirmation = input("Type CONFIRM to apply this code change: ").strip()
    except (EOFError, KeyboardInterrupt):
        return "Code change cancelled."
    if confirmation != "CONFIRM":
        return "Code change cancelled."
    try:
        CodeAgent(model=config.get("coding", {}).get("model", "qwen2.5-coder:7b")).apply(proposal)
    except Exception as error:
        return f"I could not apply that code change: {error}"
    return f"Code change applied to {edited_files}."


def run_voice_mode(config: dict, duration: int) -> None:
    from audio import record_audio_until_silence

    transcriber = SpeechToText(config["voice"].get("stt_model", "base.en"))
    print("Jarvis voice mode is ready. Speak after the prompt; I will respond when you stop.")
    while True:
        try:
            input_dir = Path(config.get("audio", {}).get("input_dir", "audio/input"))
            audio_path = input_dir / f"command-{datetime.now():%Y%m%d-%H%M%S-%f}.wav"
            print("Converting audio to text...")
            transcript = transcriber.transcribe(record_audio_until_silence(audio_path, duration))
            print(f"You said: {transcript or '[nothing detected]'}")
            if transcript:
                handle_command(transcript, config, audio_path)
        except (EOFError, KeyboardInterrupt):
            print()
            return
        except Exception as error:
            print(f"Voice command failed: {error}")


def main() -> None:
    load_dotenv()
    argument_parser = argparse.ArgumentParser(description="Jarvis-lite local voice assistant")
    argument_parser.add_argument("--config", default="config.yaml")
    argument_parser.add_argument("--text", help="Run one command without microphone input")
    argument_parser.add_argument("--voice", action="store_true", help="Listen for spoken commands")
    argument_parser.add_argument("--duration", type=int, default=5, help="Seconds to record per command")
    arguments = argument_parser.parse_args()
    config = load_config(arguments.config)

    if arguments.text:
        print(handle_command(arguments.text, config))
        return

    if arguments.voice:
        run_voice_mode(config, arguments.duration)
        return

    print("Jarvis is ready. Type a command, or press Ctrl+C to exit.")
    while True:
        try:
            command = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if command:
            print(handle_command(command, config))


if __name__ == "__main__":
    main()
