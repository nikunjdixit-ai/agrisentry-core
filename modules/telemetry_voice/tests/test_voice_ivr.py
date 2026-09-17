import os
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

from api.main import app
from modules.telemetry_voice.vernacular_voice import (
    create_voice_greeting_twiml,
    create_voice_playback_twiml,
    translate_advisory_to_hindi,
    synthesize_hindi_response,
)


class TestVoiceIVR(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    # 1. Voice greeting TwiML generation
    def test_voice_greeting_twiml_generation(self):
        twiml = create_voice_greeting_twiml(action_url="/api/voice/process-speech")
        self.assertIn("<Response>", twiml)
        self.assertIn("<Gather", twiml)
        self.assertIn('input="speech"', twiml)
        self.assertIn('action="/api/voice/process-speech"', twiml)
        self.assertIn('language="hi-IN"', twiml)
        self.assertIn("<Say", twiml)

    # 2. Voice playback TwiML generation with audio URL
    def test_voice_playback_twiml_audio(self):
        twiml = create_voice_playback_twiml(audio_url="https://example.com/audio.mp3")
        self.assertIn("<Response>", twiml)
        self.assertIn("<Play>https://example.com/audio.mp3</Play>", twiml)

    # 3. Voice playback TwiML generation with fallback speech
    def test_voice_playback_twiml_fallback(self):
        twiml = create_voice_playback_twiml(
            audio_url=None,
            fallback_text="नमस्ते किसान भाई आपकी सलाह तैयार है।"
        )
        self.assertIn("<Response>", twiml)
        self.assertIn("<Say", twiml)
        self.assertIn('language="hi-IN"', twiml)
        self.assertIn("नमस्ते किसान भाई", twiml)

    # 4. Hindi translation layer
    def test_hindi_translation_layer(self):
        diag_mock = {
            "suspected_issue": "Cotton Leaf Curl Virus",
            "actionable_advice": "Use virus-free seed, remove infected plants and control whitefly vector.",
            "telemetry": {
                "soil": {"soil_moisture": 0.16}
            },
            "weather": {
                "spraying_suitability": "Suitable"
            }
        }
        hindi_text = translate_advisory_to_hindi(diag_mock, crop="cotton")
        self.assertIn("नमस्ते किसान भाई", hindi_text)
        self.assertIn("कपास", hindi_text)
        self.assertIn("पत्ती मरोड़ रोग", hindi_text)
        self.assertIn("सफेद मक्खी", hindi_text)

    # 5. Hindi TTS synthesis
    def test_synthesize_hindi_response(self):
        result = synthesize_hindi_response("नमस्ते किसान भाई", filename_prefix="unit_test")
        self.assertTrue(result["success"])
        self.assertIn("filename", result)
        self.assertTrue(result["filename"].endswith(".mp3"))
        if result["audio_path"]:
            self.assertTrue(os.path.exists(result["audio_path"]))

    # 6. Incoming call webhook endpoint
    def test_endpoint_incoming_call(self):
        response = self.client.post(
            "/api/voice/incoming-call",
            data={
                "CallSid": "CA-TEST-001",
                "From": "+919876543210",
                "To": "+1234567890",
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/xml", response.headers["content-type"])
        self.assertIn("<Gather", response.text)
        self.assertIn('input="speech"', response.text)

    # 7. Process speech webhook endpoint
    def test_endpoint_process_speech(self):
        # Pass a simulated farmer Hindi speech query to trigger Member 2
        response = self.client.post(
            "/api/voice/process-speech",
            data={
                "CallSid": "CA-TEST-001",
                "SpeechResult": "कपास के पत्तों पर सफेद मक्खी का हमला है क्या उपाय करें",
                "Confidence": "0.92"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/xml", response.headers["content-type"])
        self.assertIn("<Response>", response.text)
        self.assertTrue("<Play>" in response.text or "<Say" in response.text)

    # 8. Empty speech fallback
    def test_endpoint_process_speech_empty(self):
        response = self.client.post(
            "/api/voice/process-speech",
            data={"SpeechResult": ""}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/xml", response.headers["content-type"])
        self.assertIn("<Say", response.text)

    # 9. Transcribe audio endpoint
    @patch("api.routes.voice.speech_to_text")
    def test_endpoint_transcribe(self, mock_stt):
        mock_stt.return_value = {
            "success": True,
            "mode": "whisper",
            "is_simulated": False,
            "language": "hi",
            "text": "कपास में सफेद मक्खी का हमला है",
            "audio_path": "sample.wav",
        }
        import io
        fake_wav = io.BytesIO(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
        response = self.client.post(
            "/api/voice/transcribe",
            files={"file": ("sample.wav", fake_wav, "audio/wav")},
            data={"language": "hi"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["transcription"]["text"], "कपास में सफेद मक्खी का हमला है")


    # 10. WhatsApp webhook endpoint
    def test_endpoint_whatsapp_webhook(self):
        response = self.client.post(
            "/api/voice/webhook/whatsapp",
            data={
                "MessageSid": "SM-TEST-WA",
                "From": "whatsapp:+919999999999",
                "Body": "फसल में कीड़ा लगा है",
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/xml", response.headers["content-type"])
        self.assertIn("<Message>", response.text)

    # 11. Call status callback endpoint
    def test_endpoint_call_status(self):
        response = self.client.post(
            "/api/voice/call-status",
            data={
                "CallSid": "CA-STATUS-01",
                "CallStatus": "completed",
                "CallDuration": "45"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "received")

    # 12. Telemetry coordinates endpoint
    def test_telemetry_with_coordinates(self):
        response = self.client.get("/api/telemetry/?latitude=28.7041&longitude=77.1025")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["latitude"], 28.7041)
        self.assertEqual(data["data"]["longitude"], 77.1025)

    # 13. Process text endpoint with default LangGraph workflow and TTS
    def test_endpoint_process_voice_default_workflow(self):
        response = self.client.post(
            "/api/voice/process",
            json={"text": "कपास के पत्तों पर सफेद मक्खी का प्रकोप है"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("hindi_advisory", data)
        self.assertIn("कपास", data["hindi_advisory"])
        self.assertIn("workflow", data)
        self.assertIn("tts", data)
        self.assertTrue(data["tts"].get("success"))

    # 14. Process text endpoint with workflow disabled
    def test_endpoint_process_voice_no_workflow(self):
        response = self.client.post(
            "/api/voice/process",
            json={"text": "नमस्ते", "run_workflow": False}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertNotIn("workflow", data)
        self.assertNotIn("hindi_advisory", data)

    # 15. Process speech endpoint with JSON payload
    def test_endpoint_process_speech_json(self):
        response = self.client.post(
            "/api/voice/process-speech",
            json={"SpeechResult": "कपास में नमी कम है"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/xml", response.headers["content-type"])
        self.assertIn("<Response>", response.text)

    # 16. Hindi TTS offline fallback test
    @patch("modules.telemetry_voice.vernacular_voice._generate_edge_tts")
    def test_tts_offline_fallback(self, mock_edge):
        mock_edge.side_effect = Exception("Network unreachable")
        res = synthesize_hindi_response("परीक्षण सलाह", filename_prefix="fallback_test")
        self.assertTrue(res["success"])
        self.assertTrue(res["is_simulated"])
        self.assertEqual(res["mode"], "mock")


if __name__ == "__main__":
    unittest.main()
