import tempfile
import unittest
from pathlib import Path

from modules.telemetry_voice.vernacular_voice import (
    get_supported_languages,
    get_tts_voice,
    text_to_speech,
    speech_to_text,
    parse_whatsapp_webhook,
    create_twiml_response,
    process_voice_message,
)


class TestVernacularVoice(unittest.TestCase):

    def test_supported_languages(self):
        languages = get_supported_languages()

        self.assertIn("hi", languages)
        self.assertIn("mr", languages)
        self.assertIn("bn", languages)
        self.assertIn("en", languages)

    def test_tts_voice(self):
        self.assertEqual(
            get_tts_voice("hi"),
            "hi-IN-MadhurNeural"
        )

    def test_unknown_language_fallback(self):
        voice = get_tts_voice("xyz")

        self.assertEqual(
            voice,
            "hi-IN-MadhurNeural"
        )

    def test_tts(self):
        result = text_to_speech(
            text="नमस्ते किसान",
            language="hi",
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["language"], "hi")

    def test_speech_to_text_missing_file(self):
        result = speech_to_text(
            "does_not_exist.wav",
            language="hi",
        )

        self.assertFalse(result["success"])

    def test_invalid_audio_format(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            path = Path(temp_dir) / "test.txt"
            path.write_text("dummy")

            result = speech_to_text(
                str(path),
                language="hi",
            )

            self.assertFalse(result["success"])

    def test_whatsapp_webhook(self):
        data = {
            "MessageSid": "SM-001",
            "From": "whatsapp:+919999999999",
            "To": "whatsapp:+918888888888",
            "Body": "Mere khet ki mitti dry hai",
            "MediaUrl0": "https://example.com/audio.ogg",
            "MediaContentType0": "audio/ogg",
        }

        result = parse_whatsapp_webhook(data)

        self.assertEqual(
            result["message_sid"],
            "SM-001"
        )

        self.assertEqual(
            result["message"],
            "Mere khet ki mitti dry hai"
        )

        self.assertTrue(result["has_media"])

    def test_twiml_response(self):
        response = create_twiml_response(
            "Aapki report receive ho gayi."
        )

        self.assertIn("<Response>", response)
        self.assertIn("<Message>", response)
        self.assertIn(
            "Aapki report receive ho gayi.",
            response
        )

    def test_twiml_with_media(self):
        response = create_twiml_response(
            "Report received",
            media_url="https://example.com/audio.mp3",
        )

        self.assertIn("<Media>", response)
        self.assertIn(
            "https://example.com/audio.mp3",
            response
        )

    def test_process_text_message(self):
        result = process_voice_message(
            text="Mitti bahut dry hai",
            language="hi",
        )

        self.assertEqual(
            result["input_type"],
            "text"
        )

        self.assertEqual(
            result["text"],
            "Mitti bahut dry hai"
        )

    def test_process_empty_message(self):
        result = process_voice_message()

        self.assertEqual(
            result["input_type"],
            "none"
        )

        self.assertIn(
            "error",
            result
        )


if __name__ == "__main__":
    unittest.main()