"""
AgriSentry Member 3 - Vernacular Voice Pipeline

Provides:
1. Speech-to-Text using Whisper when available
2. Text-to-Speech using Edge-TTS when available
3. Mock fallback when external voice tools are unavailable
4. Hindi, Marathi, Bengali and Indian English support
"""

import asyncio
from pathlib import Path
from typing import Optional

from .config import (
    DEFAULT_LANGUAGE,
    DEFAULT_TTS_VOICE,
    TTS_VOICES,
    SUPPORTED_LANGUAGES,
    VOICE_OUTPUT_DIRECTORY,
    SUPPORTED_AUDIO_FORMATS,
    ENABLE_WHISPER,
    ENABLE_EDGE_TTS,
)




def get_supported_languages():
    """Return supported language codes and names."""
    return SUPPORTED_LANGUAGES.copy()


def get_tts_voice(language: str) -> str:
    """Return Edge-TTS voice for a language."""
    language = language.lower().strip()

    if language not in TTS_VOICES:
        return DEFAULT_TTS_VOICE

    return TTS_VOICES[language]




async def _generate_edge_tts(
    text: str,
    output_path: str,
    voice: str,
):
    """Generate speech using Edge-TTS."""
    import edge_tts

    communicator = edge_tts.Communicate(
        text=text,
        voice=voice,
    )

    await communicator.save(output_path)


def text_to_speech(
    text: str,
    language: str = DEFAULT_LANGUAGE,
    output_filename: str = "agrisentry_response.mp3",
) -> dict:
    """
    Convert text to speech.

    Uses Edge-TTS when available.
    Falls back to mock audio metadata if unavailable.
    """

    output_dir = Path(VOICE_OUTPUT_DIRECTORY)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / output_filename
    voice = get_tts_voice(language)

    if ENABLE_EDGE_TTS:
        try:
            asyncio.run(
                _generate_edge_tts(
                    text=text,
                    output_path=str(output_path),
                    voice=voice,
                )
            )

            return {
                "success": True,
                "mode": "edge-tts",
                "language": language,
                "voice": voice,
                "text": text,
                "audio_path": str(output_path),
            }

        except Exception as exc:
            print(f"[TTS] Edge-TTS unavailable: {exc}")

   

    return {
        "success": True,
        "mode": "mock",
        "language": language,
        "voice": voice,
        "text": text,
        "audio_path": None,
        "message": "Mock TTS fallback used.",
    }




def speech_to_text(
    audio_path: str,
    language: Optional[str] = None,
) -> dict:
    """
    Convert speech audio into text using Whisper.

    If Whisper/audio is unavailable, returns a safe mock result.
    """

    path = Path(audio_path)

    if path.suffix.lower() not in SUPPORTED_AUDIO_FORMATS:
        return {
            "success": False,
            "mode": "validation",
            "text": "",
            "error": f"Unsupported audio format: {path.suffix}",
        }

    if not path.exists():
        return {
            "success": False,
            "mode": "validation",
            "text": "",
            "error": f"Audio file not found: {audio_path}",
        }

    if ENABLE_WHISPER:
        try:
            import whisper

            print("[STT] Loading Whisper model...")

            model = whisper.load_model("base")

            result = model.transcribe(
                str(path),
                language=language if language else None,
            )

            return {
                "success": True,
                "mode": "whisper",
                "language": language,
                "text": result.get("text", "").strip(),
                "audio_path": str(path),
            }

        except Exception as exc:
            print(f"[STT] Whisper unavailable: {exc}")

   

    return {
        "success": True,
        "mode": "mock",
        "language": language,
        "text": "Mock farmer voice message for AgriSentry.",
        "audio_path": str(path),
    }




def parse_whatsapp_webhook(form_data: dict) -> dict:
    """
    Parse common Twilio WhatsApp webhook fields.

    Expected fields may include:
    MediaUrl0
    From
    To
    MessageSid
    Body
    """

    return {
        "message_sid": form_data.get("MessageSid"),
        "from": form_data.get("From"),
        "to": form_data.get("To"),
        "message": form_data.get("Body", ""),
        "media_url": form_data.get("MediaUrl0"),
        "media_content_type": form_data.get("MediaContentType0"),
        "has_media": bool(form_data.get("MediaUrl0")),
    }




def create_twiml_response(
    message: str,
    media_url: Optional[str] = None,
) -> str:
    """
    Create a simple TwiML XML response.
    """

    safe_message = (
        str(message)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    response = "<Response>"
    response += "<Message>"
    response += f"<Body>{safe_message}</Body>"

    if media_url:
        response += f"<Media>{media_url}</Media>"

    response += "</Message>"
    response += "</Response>"

    return response




def process_voice_message(
    text: Optional[str] = None,
    audio_path: Optional[str] = None,
    language: str = DEFAULT_LANGUAGE,
) -> dict:
    """
    Process either text or audio input.

    Audio:
        Speech-to-text

    Text:
        Ready for AI processing
    """

    if audio_path:
        transcription = speech_to_text(
            audio_path=audio_path,
            language=language,
        )

        return {
            "input_type": "audio",
            "language": language,
            "transcription": transcription,
        }

    if text:
        return {
            "input_type": "text",
            "language": language,
            "text": text,
        }

    return {
        "input_type": "none",
        "language": language,
        "error": "No text or audio input provided.",
    }




if __name__ == "__main__":

    print("=" * 60)
    print("AGRISENTRY - VERNACULAR VOICE DEMO")
    print("=" * 60)

    print("\nSupported languages:")
    for code, name in get_supported_languages().items():
        print(f"  {code} -> {name} -> {get_tts_voice(code)}")

    print("\nGenerating Hindi TTS...")

    tts_result = text_to_speech(
        text="आपके खेत में मिट्टी की नमी कम है।",
        language="hi",
    )

    print(tts_result)

    print("\nTesting WhatsApp webhook parser...")

    webhook_data = {
        "MessageSid": "SM-DEMO-001",
        "From": "whatsapp:+919999999999",
        "To": "whatsapp:+918888888888",
        "Body": "मेरे खेत की मिट्टी बहुत सूखी है।",
        "MediaUrl0": "https://example.com/farmer-audio.ogg",
        "MediaContentType0": "audio/ogg",
    }

    parsed = parse_whatsapp_webhook(webhook_data)

    print(parsed)

    print("\nTwiML response:")

    twiml = create_twiml_response(
        "आपकी रिपोर्ट प्राप्त हो गई है।",
    )

    print(twiml)

    print("\nVoice pipeline demo completed.")