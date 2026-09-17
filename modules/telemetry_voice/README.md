# 📡 AgriSentry — Member 3: Telemetry, Vernacular Voice & Telephony IVR

This module powers AgriSentry's field environmental intelligence, edge gateway telemetry, and real-time interactive vernacular voice telephony (IVR) designed for Indian farmers speaking in Hindi.

---

## 🏗️ Architecture Overview

```
                               ┌────────────────────────┐
                               │  Farmer's Phone Call   │
                               │   (Inbound Cellular)   │
                               └───────────┬────────────┘
                                           │
                                           ▼
                               ┌────────────────────────┐
                               │   Twilio Voice API     │
                               └───────────┬────────────┘
                                           │ POST /api/voice/incoming-call
                                           ▼
                               ┌────────────────────────┐
                               │  AgriSentry IVR Entry  │
                               │   (Hindi <Gather>)     │
                               └───────────┬────────────┘
                                           │ Farmer speaks Hindi
                                           │ POST /api/voice/process-speech
                                           ▼
  ┌───────────────────────┐    ┌────────────────────────┐    ┌───────────────────────┐
  │ Open-Meteo & Virtual  │───►│   Member 2 LangGraph   │◄───│ AgroRAG Knowledge     │
  │ Sensing (Soil/Weather)│    │    Multi-Agent Core    │    │ (ICAR Advisory Base)  │
  └───────────────────────┘    └───────────┬────────────┘    └───────────────────────┘
                                           │ English Diagnostic Output
                                           ▼
                               ┌────────────────────────┐
                               │ Hindi Advisory Adapter │
                               │(Vernacular Translation)│
                               └───────────┬────────────┘
                                           │ Natural Hindi Sentences
                                           ▼
                               ┌────────────────────────┐
                               │   Edge-TTS Synthesis   │
                               │ (hi-IN-MadhurNeural)   │
                               └───────────┬────────────┘
                                           │ voice_outputs/*.mp3
                                           ▼
                               ┌────────────────────────┐
                               │  Twilio Voice Playback │
                               │   (<Play> / <Say>)     │
                               └───────────┬────────────┘
                                           │ Audio Stream
                                           ▼
                               ┌────────────────────────┐
                               │  Farmer Hears Advice   │
                               └────────────────────────┘
```

---

## 🚀 API Endpoints Reference

### 1. Telemetry Endpoints

#### `GET /api/telemetry/`
Fetches combined agro-climatic sensing data (soil moisture, temperature, relative humidity, precipitation, and NDVI canopy index).
* **Query Parameters (Optional):**
  * `latitude` (float): GPS latitude (defaults to `26.8467` for Lucknow/Barabanki).
  * `longitude` (float): GPS longitude (defaults to `80.9462`).
* **Response (JSON):**
  ```json
  {
    "status": "success",
    "data": {
      "latitude": 26.8467,
      "longitude": 80.9462,
      "soil": {
        "soil_moisture": 0.17,
        "soil_temperature": 29.1,
        "ambient_temperature": 27.8,
        "relative_humidity": 84.0,
        "precipitation": 0.0,
        "source": "Open-Meteo",
        "is_simulated": false
      },
      "ndvi": {
        "ndvi_mean": 0.45,
        "vegetation_class": "Moderate / Developing Vegetation",
        "source": "Synthetic Sentinel-2 Reflectance Simulator",
        "is_simulated": true
      }
    }
  }
  ```

---

### 2. Telephony & Voice IVR Endpoints

#### `POST /api/voice/incoming-call`
Twilio Voice webhook entrypoint when a farmer dials the AgriSentry helpline.
* **Content-Type:** `application/x-www-form-urlencoded`
* **Response:** Twilio Voice XML (TwiML) with Hindi greeting and `<Gather input="speech">`:
  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <Response>
      <Say language="hi-IN" voice="Polly.Aditi">नमस्ते, एग्रीसेंट्री कृषि हेल्पलाइन में आपका स्वागत है। कृपया बीप के बाद अपनी फसल या कीट की समस्या बताएं।</Say>
      <Gather input="speech" action="/api/voice/process-speech" method="POST" language="hi-IN" speechTimeout="auto">
          <Say language="hi-IN" voice="Polly.Aditi">कृपया बोलें...</Say>
      </Gather>
      <Say language="hi-IN" voice="Polly.Aditi">हमें आपकी आवाज नहीं सुनाई दी। कृपया दोबारा कॉल करें। धन्यवाद।</Say>
  </Response>
  ```

#### `POST /api/voice/process-speech`
Webhook called by Twilio when the caller finishes speaking.
* **Payload:** Twilio Form parameters (`SpeechResult`, `Confidence`, `CallSid`, `From`).
* **Execution Flow:**
  1. Extracts transcribed Hindi speech from `SpeechResult`.
  2. Detects crop (`cotton`, `tomato`, `apple`, etc.) and region (`Punjab`, `Uttar Pradesh`, etc.).
  3. Injects user query and crop into `AgriSentryState` and executes `graph_app.invoke()`.
  4. Translates Member 2 diagnostic recommendations into natural, respectful Hindi.
  5. Synthesizes an MP3 audio file via Edge-TTS (`hi-IN-MadhurNeural`) saved in `voice_outputs/`.
  6. Returns Voice TwiML containing `<Play>{PUBLIC_BASE_URL}/voice_outputs/{file}.mp3</Play>` (or `<Say>` fallback if public base URL is not configured).

#### `POST /api/voice/transcribe`
File upload endpoint for WhatsApp voice notes or phone recording files.
* **Content-Type:** `multipart/form-data`
* **Parameters:** `file: UploadFile` (`.wav`, `.mp3`, `.ogg`, `.m4a`), `language: str` (default: `"hi"`).
* **Execution:** Transcribes speech audio using OpenAI Whisper with automatic fallback.

#### `POST /api/voice/webhook/whatsapp`
Webhook for Twilio WhatsApp messaging integration.
* **Payload:** WhatsApp webhook form fields (`From`, `Body`, `MediaUrl0`).
* **Response:** Messaging TwiML (`<Response><Message><Body>...</Body></Message></Response>`).

#### `POST /api/voice/call-status`
Webhook for Twilio call lifecycle updates (`initiated`, `ringing`, `answered`, `completed`).
* **Payload:** Form parameters (`CallSid`, `CallStatus`, `CallDuration`).

#### `POST /api/voice/process`
Backward-compatible JSON text endpoint for testing voice messaging logic.
* **Payload:** `{"text": "कपास में सफेद मक्खी", "language": "hi", "run_workflow": true}`.

---

## ⚙️ Environment Configuration

Copy `.env.example` to `.env` and set your credentials:

```bash
cp .env.example .env
```

| Variable | Description | Required For |
|---|---|---|
| `TWILIO_ACCOUNT_SID` | Your Twilio Account SID (`AC...`) | Live phone calls |
| `TWILIO_AUTH_TOKEN` | Your Twilio Auth Token | Live phone calls |
| `TWILIO_PHONE_NUMBER` | Your Twilio purchased phone number (`+1...` or `+91...`) | Live phone calls |
| `PUBLIC_BASE_URL` | Public HTTPS URL where Twilio can reach this server (e.g., ngrok) | Serving `<Play>` audio to callers |
| `DEFAULT_VOICE_CROP` | Fallback crop if caller doesn't mention one (default: `cotton`) | Member 2 diagnosis |
| `DEFAULT_VOICE_REGION` | Fallback region if caller doesn't mention one (default: `Punjab`) | Member 2 diagnosis |

> **Note on Local Testing**:
> If `PUBLIC_BASE_URL` is not set, the IVR automatically falls back to speaking the Hindi response directly via Twilio's built-in `<Say language="hi-IN" voice="Polly.Aditi">` engine, so the caller will still hear the advice clearly over the phone even without exposing static audio files!

---

## 🌐 Connecting Twilio Voice to Local Server (Live Phone Testing)

To test a live cellular phone call from a physical mobile phone to AgriSentry:

1. **Start the FastAPI server**:
   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```

2. **Expose your local server to the Internet**:
   Using [ngrok](https://ngrok.com/):
   ```bash
   ngrok http 8000
   ```
   Copy the Forwarding HTTPS URL (e.g., `https://9a4b-123.ngrok-free.app`).

3. **Set your environment variable**:
   In your `.env` file:
   ```env
   PUBLIC_BASE_URL=https://9a4b-123.ngrok-free.app
   ```

4. **Configure the Twilio Console**:
   * Log into [Twilio Console](https://console.twilio.com/).
   * Navigate to **Phone Numbers** $\rightarrow$ **Manage** $\rightarrow$ **Active Numbers**.
   * Click on your phone number.
   * Under **Voice & Fax** $\rightarrow$ **A CALL COMES IN**:
     * Select **Webhook**.
     * URL: `https://9a4b-123.ngrok-free.app/api/voice/incoming-call`
     * HTTP Method: `HTTP POST`
   * Click **Save configuration**.

5. **Make the Call**:
   Dial the Twilio phone number from any cellular or landline phone. Speak your crop issue in Hindi (e.g., *"कपास में सफेद मक्खी लग गई है"*). AgriSentry will process your query, fetch live telemetry, retrieve ICAR advisories, and speak the recommendation back to you in Hindi!

---

## 🎙️ Speech-to-Text (Whisper) & Text-to-Speech (Edge-TTS)

* **Edge-TTS**: Uses Microsoft Edge neural voice synthesis (`hi-IN-MadhurNeural` for Hindi, `mr-IN-AarohiNeural` for Marathi, `bn-IN-BashkarNeural` for Bengali). Works out of the box without requiring API keys.
* **Whisper**: Uses OpenAI Whisper (`base` or `tiny` model). When audio files are uploaded to `/api/voice/transcribe`, Whisper transcribes the speech. If Whisper or audio drivers are not available, it safely falls back to synthetic mock output with `is_simulated: true`.

---

## ⚠️ Known Limitations & Simulation Transparency

1. **NDVI Simulation**:
   The current NDVI index pipeline uses `generate_ndvi_fallback()`, an agro-climatic pseudo-random simulation modeling typical vegetative index dynamics. **It is NOT connected to live Copernicus/Sentinel-2 satellite imagery APIs.** The outputs are explicitly tagged with `source: "Synthetic Sentinel-2 Reflectance Simulator"` and `is_simulated: true`.
2. **Cellular Phone Calls**:
   Receiving actual inbound phone calls requires a valid Twilio account, an active phone number, and a public tunnel (`PUBLIC_BASE_URL`) forwarding requests to the FastAPI backend.
