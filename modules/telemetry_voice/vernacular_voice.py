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
import time
from typing import Optional, Dict, Any
import uuid

from .config import (
    DEFAULT_LANGUAGE,
    DEFAULT_TTS_VOICE,
    TTS_VOICES,
    SUPPORTED_LANGUAGES,
    VOICE_OUTPUT_DIRECTORY,
    SUPPORTED_AUDIO_FORMATS,
    ENABLE_WHISPER,
    ENABLE_EDGE_TTS,
    TWILIO_VOICE_LANGUAGE,
    TWILIO_VOICE_ACTOR,
    PUBLIC_BASE_URL,
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


def _run_async_coroutine(coro):
    """Run an async coroutine safely whether an event loop is already running or not."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)


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
            _run_async_coroutine(
                _generate_edge_tts(
                    text=text,
                    output_path=str(output_path),
                    voice=voice,
                )
            )


            return {
                "success": True,
                "mode": "edge-tts",
                "is_simulated": False,
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
        "is_simulated": True,
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
                "is_simulated": False,
                "language": language,
                "text": result.get("text", "").strip(),
                "audio_path": str(path),
            }

        except Exception as exc:
            print(f"[STT] Whisper unavailable: {exc}")

   

    return {
        "success": True,
        "mode": "mock",
        "is_simulated": True,
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


def _escape_xml(text: str) -> str:
    """Safely escape XML characters for TwiML."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def create_voice_greeting_twiml(
    action_url: str,
    prompt_text: Optional[str] = None,
) -> str:
    """
    Create Twilio Voice TwiML greeting with <Gather input="speech">.
    Asks the caller to speak their agricultural query in Hindi.
    """
    greeting = (
        prompt_text
        or "नमस्ते, एग्रीसेंट्री कृषि हेल्पलाइन में आपका स्वागत है। कृपया बीप के बाद अपनी फसल या कीट की समस्या बताएं।"
    )
    safe_greeting = _escape_xml(greeting)

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Response>\n'
        f'    <Say language="{TWILIO_VOICE_LANGUAGE}" voice="{TWILIO_VOICE_ACTOR}">{safe_greeting}</Say>\n'
        f'    <Gather input="speech" action="{action_url}" method="POST" language="{TWILIO_VOICE_LANGUAGE}" speechTimeout="auto">\n'
        f'        <Say language="{TWILIO_VOICE_LANGUAGE}" voice="{TWILIO_VOICE_ACTOR}">कृपया बोलें...</Say>\n'
        '    </Gather>\n'
        f'    <Say language="{TWILIO_VOICE_LANGUAGE}" voice="{TWILIO_VOICE_ACTOR}">हमें आपकी आवाज नहीं सुनाई दी। कृपया दोबारा कॉल करें। धन्यवाद।</Say>\n'
        '</Response>'
    )


def create_voice_playback_twiml(
    audio_url: Optional[str] = None,
    fallback_text: Optional[str] = None,
) -> str:
    """
    Create Twilio Voice TwiML response.
    Uses <Play> if an audio URL is available; falls back to <Say> with Hindi voice.
    """
    twiml = '<?xml version="1.0" encoding="UTF-8"?>\n<Response>\n'
    if audio_url:
        twiml += f'    <Play>{audio_url}</Play>\n'
    if fallback_text:
        safe_text = _escape_xml(fallback_text)
        if not audio_url:
            twiml += f'    <Say language="{TWILIO_VOICE_LANGUAGE}" voice="{TWILIO_VOICE_ACTOR}">{safe_text}</Say>\n'
    if not audio_url and not fallback_text:
        twiml += f'    <Say language="{TWILIO_VOICE_LANGUAGE}" voice="{TWILIO_VOICE_ACTOR}">आपकी फसल सलाह तैयार है। धन्यवाद।</Say>\n'
    twiml += '</Response>'
    return twiml


CROP_TRANSLATIONS = {
    "cotton": "कपास",
    "tomato": "टमाटर",
    "apple": "सेब",
    "potato": "आलू",
    "corn": "मक्का",
    "maize": "मक्का",
    "rice": "धान",
    "paddy": "धान",
    "wheat": "गेहूं",
    "grape": "अंगूर",
    "chilli": "मिर्च",
    "pepper": "शिमला मिर्च",
    "soybean": "सोयाबीन",
    "sugarcane": "गन्ना",
}

DISEASE_TRANSLATIONS = {
    "cotton leaf curl virus": "कपास का पत्ती मरोड़ रोग",
    "whitefly": "सफेद मक्खी कीट का प्रकोप",
    "bacterial spot": "जीवाणु धब्बा रोग",
    "early blight": "अगेती झुलसा रोग",
    "late blight": "पछेती झुलसा रोग",
    "powdery mildew": "चूर्णिल फफूंद रोग",
    "septoria leaf spot": "सेप्टोरिया पत्ती धब्बा रोग",
    "leaf mold": "पत्ती फफूंद रोग",
    "apple scab": "सेब का स्कैब रोग",
    "cedar apple rust": "सेब का रतुआ रोग",
    "black rot": "काला सड़न रोग",
    "common rust": "सामान्य रतुआ रोग",
}

ADVICE_TRANSLATIONS = {
    "use virus-free seed, remove infected plants and control whitefly vector.": (
        "प्रमाणित रोगमुक्त बीज का उपयोग करें, खेत से संक्रमित पौधों को तुरंत उखाड़कर नष्ट करें, "
        "और सफेद मक्खी कीट की रोकथाम के लिए अनुशंसित कीटनाशक का छिड़काव करें।"
    ),
    "consult local agricultural extension officer.": (
        "सटीक उपचार और कीटनाशक की मात्रा के लिए अपने नजदीकी कृषि विज्ञान केंद्र या कृषि प्रसार अधिकारी से संपर्क करें।"
    ),
}


def translate_advisory_to_hindi(
    diagnostic_result: Dict[str, Any],
    crop: str = "cotton",
) -> str:
    """
    Convert Member 2 diagnostic outputs into natural, farmer-friendly Hindi.
    Integrates diagnosis, actionable advice, and field telemetry/weather signals.
    """
    if not isinstance(diagnostic_result, dict):
        return "नमस्ते किसान भाई। आपकी फसल रिपोर्ट प्राप्त हो गई है। कृपया नजदीकी कृषि अधिकारी से संपर्क करें।"

    norm_crop = crop.strip().lower()
    hindi_crop = CROP_TRANSLATIONS.get(norm_crop, norm_crop)

    # 1. Identify disease / issue
    suspected_issue = diagnostic_result.get("suspected_issue") or ""
    if not suspected_issue:
        treatment_advisories = diagnostic_result.get("treatment_advisories") or []
        if treatment_advisories:
            suspected_issue = treatment_advisories[0]

    norm_issue = str(suspected_issue).strip().lower()
    hindi_issue = None
    for k, v in DISEASE_TRANSLATIONS.items():
        if k in norm_issue:
            hindi_issue = v
            break
    if not hindi_issue:
        hindi_issue = suspected_issue or "फसल समस्या"

    # 2. Identify actionable advice
    raw_advice = diagnostic_result.get("actionable_advice") or diagnostic_result.get("primary_advisory") or ""
    norm_advice = str(raw_advice).strip().lower()

    hindi_advice = None
    for k, v in ADVICE_TRANSLATIONS.items():
        if k in norm_advice:
            hindi_advice = v
            break

    if not hindi_advice:
        if "whitefly" in norm_advice:
            hindi_advice = "सफेद मक्खी नियंत्रण के लिए इमिडाक्लोप्रिड या नीम तेल का उचित मात्रा में छिड़काव करें।"
        elif "fungicide" in norm_advice or "blight" in norm_advice:
            hindi_advice = "फफूंदनाशक दवा का छिड़काव करें और खेत में जलभराव न होने दें।"
        elif raw_advice:
            hindi_advice = f"{raw_advice}। अधिक जानकारी के लिए कृषि अधिकारी से सलाह लें।"
        else:
            hindi_advice = "प्रमाणित कीटनाशक का उपयोग करें और नजदीकी कृषि विज्ञान केंद्र से संपर्क करें।"

    # 3. Telemetry & weather context
    field_signals_hindi = []
    telemetry = diagnostic_result.get("telemetry", {})
    soil_data = telemetry.get("soil", {}) if isinstance(telemetry, dict) else {}
    soil_moist = soil_data.get("soil_moisture")
    if soil_moist is not None:
        try:
            if float(soil_moist) < 0.20:
                field_signals_hindi.append("मिट्टी में नमी कम है, पहले हल्की सिंचाई करें")
            elif float(soil_moist) > 0.40:
                field_signals_hindi.append("खेत में नमी अधिक है, जल निकासी पर ध्यान दें")
        except (ValueError, TypeError):
            pass

    weather = diagnostic_result.get("weather", {})
    if isinstance(weather, dict):
        spraying = weather.get("spraying_suitability")
        if spraying == "Suitable":
            field_signals_hindi.append("छिड़काव के लिए मौसम अनुकूल है")

    # 4. Construct natural Hindi speech text
    parts = [
        "नमस्ते किसान भाई।",
        f"आपकी {hindi_crop} की फसल में {hindi_issue} के लक्षण पाए गए हैं।",
        f"सलाह: {hindi_advice}",
    ]

    if field_signals_hindi:
        parts.append(f"खेत की स्थिति: {', '.join(field_signals_hindi)}।")

    parts.append("एग्रीसेंट्री का उपयोग करने के लिए धन्यवाद।")

    return " ".join(parts)


def synthesize_hindi_response(
    text: str,
    filename_prefix: str = "advisory",
) -> Dict[str, Any]:
    """
    Generate an audio file in Hindi using Edge-TTS and return metadata
    including local audio path and public/relative URL for Twilio.
    """
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:6]
    filename = f"{filename_prefix}_{timestamp}_{unique_id}.mp3"

    tts_result = text_to_speech(
        text=text,
        language="hi",
        output_filename=filename,
    )

    audio_path = tts_result.get("audio_path")
    audio_url = None
    if audio_path:
        relative_url = f"/voice_outputs/{filename}"
        if PUBLIC_BASE_URL:
            audio_url = f"{PUBLIC_BASE_URL}{relative_url}"
        else:
            audio_url = relative_url

    return {
        "success": tts_result.get("success", False),
        "mode": tts_result.get("mode"),
        "is_simulated": tts_result.get("is_simulated", False),
        "filename": filename,
        "audio_path": audio_path,
        "audio_url": audio_url,
        "text": text,
    }




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