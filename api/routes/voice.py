from fastapi import APIRouter
from pydantic import BaseModel

from modules.telemetry_voice.vernacular_voice import process_voice_message


router = APIRouter(
    prefix="/api/voice",
    tags=["Voice"]
)


class VoiceRequest(BaseModel):
    text: str
    language: str = "hi"


@router.post("/process")
def process_voice(request: VoiceRequest):
    result = process_voice_message(
        text=request.text,
        language=request.language
    )

    return {
        "status": "success",
        "result": result
    }