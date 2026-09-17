import logging
from pathlib import Path
import tempfile
from typing import Any, Dict, Optional, cast

from fastapi import APIRouter, File, Form, HTTPException, Request, Response, UploadFile
from pydantic import BaseModel, Field

from api.agents.graph import app as graph_app, AgriSentryState
from modules.telemetry_voice.config import (
    DEFAULT_VOICE_CROP,
    DEFAULT_VOICE_REGION,
    PUBLIC_BASE_URL,
    VOICE_OUTPUT_DIRECTORY,
)
from modules.telemetry_voice.vernacular_voice import (
    create_twiml_response,
    create_voice_greeting_twiml,
    create_voice_playback_twiml,
    parse_whatsapp_webhook,
    process_voice_message,
    speech_to_text,
    synthesize_hindi_response,
    translate_advisory_to_hindi,
)

logger = logging.getLogger("agrisentry.voice")

router = APIRouter(
    prefix="/api/voice",
    tags=["Voice"],
)


class VoiceRequest(BaseModel):
    text: str
    language: str = "hi"
    crop: Optional[str] = None
    region: Optional[str] = None
    run_workflow: bool = True


def _detect_crop_and_region(
    text: str,
    default_crop: str = DEFAULT_VOICE_CROP,
    default_region: str = DEFAULT_VOICE_REGION,
) -> tuple[str, str]:
    """Detect crop and region from farmer spoken query or use defaults."""
    lower = text.lower()
    crop = default_crop
    region = default_region

    if "कपास" in lower or "cotton" in lower:
        crop = "cotton"
    elif "टमाटर" in lower or "tomato" in lower:
        crop = "tomato"
    elif "आलू" in lower or "potato" in lower:
        crop = "potato"
    elif "सेब" in lower or "apple" in lower:
        crop = "apple"
    elif "मक्का" in lower or "corn" in lower:
        crop = "corn"
    elif "धान" in lower or "rice" in lower or "paddy" in lower:
        crop = "rice"
    elif "गेहूं" in lower or "wheat" in lower:
        crop = "wheat"

    if "punjab" in lower or "पंजाब" in lower:
        region = "Punjab"
    elif "uttar pradesh" in lower or "उत्तर प्रदेश" in lower or "up" in lower:
        region = "Uttar Pradesh"
    elif "haryana" in lower or "हरियाणा" in lower:
        region = "Haryana"

    return crop, region


@router.post("/process")
def process_voice(request: VoiceRequest) -> Dict[str, Any]:
    """
    Process text query through the vernacular pipeline.
    By default executes the Member 2 LangGraph workflow and returns Hindi advisory and TTS audio.
    """
    result = process_voice_message(
        text=request.text,
        language=request.language,
    )

    response_data: Dict[str, Any] = {
        "status": "success",
        "result": result,
    }

    if request.run_workflow:
        detected_crop, detected_region = _detect_crop_and_region(request.text)
        crop = request.crop or detected_crop
        region = request.region or detected_region
        state: AgriSentryState = {
            "user_query": request.text,
            "crop_details": {"crop": crop, "region": region},
            "diagnostic_result": None,
            "rag_context": [],
            "vendor_options": [],
            "mandi_prices": {},
            "telemetry_context": {},
            "current_step": "voice_request_received",
            "verification_flag": False,
            "retry_count": 0,
            "verification_notes": "",
            "evidence_score": 0.0,
        }
        workflow_res = graph_app.invoke(cast(Any, state))
        diagnostic_res = workflow_res.get("diagnostic_result", {})
        hindi_advice = translate_advisory_to_hindi(
            diagnostic_res,
            crop=crop,
        )
        tts_meta = synthesize_hindi_response(
            hindi_advice,
            filename_prefix=f"voice_{crop}",
        )

        response_data["crop"] = crop
        response_data["region"] = region
        response_data["workflow"] = workflow_res
        response_data["hindi_advisory"] = hindi_advice
        response_data["tts"] = tts_meta
        if tts_meta.get("audio_url"):
            response_data["audio_url"] = tts_meta["audio_url"]

    return response_data


# ------------------------------------------------------------
# 1. Twilio Voice Call - Incoming Call Webhook (IVR Entrypoint)
# ------------------------------------------------------------
@router.post("/incoming-call")
async def incoming_call(request: Request) -> Response:
    """
    Twilio Voice incoming call webhook.
    Returns TwiML with <Say> greeting in Hindi and <Gather input="speech">.
    """
    try:
        form = await request.form()
        call_sid = form.get("CallSid", "UNKNOWN")
        caller = form.get("From", "ANONYMOUS")
        logger.info("Incoming phone call received: CallSid=%s, From=%s", call_sid, caller)
    except Exception:
        pass

    action_url = "/api/voice/process-speech"
    if PUBLIC_BASE_URL:
        action_url = f"{PUBLIC_BASE_URL}/api/voice/process-speech"

    twiml = create_voice_greeting_twiml(action_url=action_url)
    return Response(content=twiml, media_type="application/xml")


# ------------------------------------------------------------
# 2. Twilio Voice Call - Process Speech & Member 2 Integration
# ------------------------------------------------------------
@router.post("/process-speech")
async def process_speech(request: Request) -> Response:
    """
    Twilio Voice speech result webhook.
    Receives farmer Hindi speech, invokes Member 2 / LangGraph,
    synthesizes spoken Hindi advice via Edge-TTS, and plays back via TwiML.
    """
    speech_result = ""
    try:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            body = await request.json()
            speech_result = body.get("SpeechResult") or body.get("speech_result", "")
        else:
            form = await request.form()
            speech_result = str(form.get("SpeechResult", "")).strip()
    except Exception as exc:
        logger.warning("Error reading speech request: %s", exc)

    if not speech_result:
        fallback_twiml = create_voice_playback_twiml(
            audio_url=None,
            fallback_text="हमें आपकी आवाज स्पष्ट सुनाई नहीं दी। कृपया दोबारा कॉल करें।",
        )
        return Response(content=fallback_twiml, media_type="application/xml")

    # 1. Infer crop & region or fallback to defaults
    crop, region = _detect_crop_and_region(speech_result)

    # 2. Connect to Member 2 / LangGraph workflow
    state: AgriSentryState = {
        "user_query": speech_result,
        "crop_details": {
            "crop": crop,
            "region": region,
        },
        "diagnostic_result": None,
        "rag_context": [],
        "vendor_options": [],
        "mandi_prices": {},
        "telemetry_context": {},
        "current_step": "voice_call_received",
        "verification_flag": False,
        "retry_count": 0,
        "verification_notes": "",
        "evidence_score": 0.0,
    }

    try:
        workflow_result = graph_app.invoke(cast(Any, state))
        diagnostic_result = workflow_result.get("diagnostic_result", {})
    except Exception as exc:
        logger.error("Member 2 workflow execution failed: %s", exc)
        diagnostic_result = {
            "suspected_issue": "फसल परामर्श",
            "actionable_advice": "Consult local agricultural extension officer.",
        }

    # 3. Translate Member 2 output to natural Hindi
    hindi_text = translate_advisory_to_hindi(diagnostic_result, crop=crop)

    # 4. Generate Hindi TTS audio file via Edge-TTS
    audio_url = None
    try:
        tts_meta = synthesize_hindi_response(hindi_text, filename_prefix=f"call_{crop}")
        if PUBLIC_BASE_URL and tts_meta.get("audio_url"):
            audio_url = tts_meta.get("audio_url")
    except Exception as exc:
        logger.error("TTS generation failed: %s", exc)

    # 5. Return Voice TwiML with <Play> or <Say> fallback
    response_twiml = create_voice_playback_twiml(
        audio_url=audio_url,
        fallback_text=hindi_text,
    )
    return Response(content=response_twiml, media_type="application/xml")


# ------------------------------------------------------------
# 3. Audio Upload / Whisper Transcription Endpoint
# ------------------------------------------------------------
@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("hi"),
) -> Dict[str, Any]:
    """
    Upload an audio file (e.g. WhatsApp voice note or phone recording)
    and transcribe it using Whisper with mock fallback.
    """
    suffix = Path(file.filename or "audio.wav").suffix.lower()
    if suffix not in [".wav", ".mp3", ".ogg", ".m4a"]:
        suffix = ".wav"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
        temp_path = temp_audio.name
        content = await file.read()
        temp_audio.write(content)

    try:
        result = speech_to_text(temp_path, language=language)
        return {
            "status": "success" if result.get("success") else "error",
            "filename": file.filename,
            "transcription": result,
        }
    finally:
        try:
            Path(temp_path).unlink(missing_ok=True)
        except Exception:
            pass


# ------------------------------------------------------------
# 4. WhatsApp Webhook Endpoint
# ------------------------------------------------------------
@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request) -> Response:
    """
    Twilio WhatsApp webhook handler.
    Receives farmer text or voice note metadata, parses with
    parse_whatsapp_webhook, and returns messaging TwiML.
    """
    form_data = dict(await request.form())
    parsed = parse_whatsapp_webhook(form_data)
    logger.info("WhatsApp webhook received: From=%s, HasMedia=%s", parsed.get("from"), parsed.get("has_media"))

    response_msg = "नमस्ते किसान भाई, एग्रीसेंट्री को आपकी रिपोर्ट प्राप्त हो गई है। हम जल्द ही आपकी सहायता करेंगे।"
    twiml = create_twiml_response(response_msg)
    return Response(content=twiml, media_type="application/xml")


# ------------------------------------------------------------
# 5. Call Status Callback Endpoint
# ------------------------------------------------------------
@router.post("/call-status")
async def call_status_callback(request: Request) -> Dict[str, Any]:
    """
    Twilio call status callback handler (initiated, ringing, answered, completed).
    Safely logs call lifecycle events.
    """
    try:
        form = dict(await request.form())
        call_sid = form.get("CallSid", "UNKNOWN")
        status = form.get("CallStatus", "UNKNOWN")
        duration = form.get("CallDuration", "0")
        logger.info("Call status update: CallSid=%s, Status=%s, Duration=%ss", call_sid, status, duration)
        return {
            "status": "received",
            "call_sid": call_sid,
            "call_status": status,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}