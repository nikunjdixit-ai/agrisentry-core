"""
AgriSentry - Member 3
Unified Simulation Driver

Runs:
1. Virtual Sensing
2. Edge Gateway & LoRaWAN Simulation
3. Vernacular Voice Pipeline

All systems work without requiring:
- Physical sensors
- LoRaWAN hardware
- MQTT broker
- Real farmer audio
"""

from .config import (
    DEFAULT_LATITUDE,
    DEFAULT_LONGITUDE,
)

from .virtual_sensing import (
    get_unified_virtual_sensing,
)

from .edge_gateway_sim import (
    create_default_gateway,
)

from .vernacular_voice import (
    text_to_speech,
    parse_whatsapp_webhook,
    create_twiml_response,
)


def print_header(title: str) -> None:
    """Print a section header."""

    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def run_virtual_sensing_demo() -> None:
    """Run virtual soil, weather and satellite sensing."""

    print_header("1. VIRTUAL SENSING")

    try:
        sensing = get_unified_virtual_sensing(
            DEFAULT_LATITUDE,
            DEFAULT_LONGITUDE,
        )

        print("Location:")
        print(f"  Latitude  : {sensing.latitude}")
        print(f"  Longitude : {sensing.longitude}")

        print("\nSoil / Weather Telemetry:")

        print(
            f"  Soil Moisture    : "
            f"{sensing.soil.soil_moisture} m³/m³"
        )

        print(
            f"  Soil Temperature : "
            f"{sensing.soil.soil_temperature} °C"
        )

        print(
            f"  Ambient Temp     : "
            f"{sensing.soil.ambient_temperature} °C"
        )

        print(
            f"  Humidity         : "
            f"{sensing.soil.relative_humidity}%"
        )

        print(
            f"  Precipitation    : "
            f"{sensing.soil.precipitation} mm"
        )

        print(
            f"  Source           : "
            f"{sensing.soil.source}"
        )

        print(
            f"  Simulated        : "
            f"{sensing.soil.is_simulated}"
        )

        print("\nSatellite / NDVI Telemetry:")

        print(
            f"  NDVI Mean        : "
            f"{sensing.ndvi.ndvi_mean}"
        )

        print(
            f"  NDVI Min         : "
            f"{sensing.ndvi.ndvi_min}"
        )

        print(
            f"  NDVI Max         : "
            f"{sensing.ndvi.ndvi_max}"
        )

        print(
            f"  Cloud Cover      : "
            f"{sensing.ndvi.cloud_cover}%"
        )

        print(
            f"  Vegetation Class : "
            f"{sensing.ndvi.vegetation_class}"
        )

        print(
            f"  Source           : "
            f"{sensing.ndvi.source}"
        )

        print("\n[Virtual Sensing] SUCCESS")

    except Exception as exc:
        print(f"[Virtual Sensing Error] {exc}")


def run_edge_gateway_demo() -> None:
    """Run farm sensor and village gateway simulation."""

    print_header("2. EDGE GATEWAY SIMULATION")

    try:
        gateway = create_default_gateway()

        print("Gateway ID:")
        print(f"  {gateway.gateway_id}")

        print("\nTransport:")
        print(f"  {gateway.transport}")

        print("\nConnected Farm Nodes:")

        for node in gateway.nodes:
            print(f"  - {node.node_id}")

        packets = gateway.broadcast_once()

        print(
            f"\nPackets received: "
            f"{gateway.packets_received}"
        )

        print("\nTelemetry Packets:")

        for packet in packets:

            print(
                f"\n  Node ID          : "
                f"{packet.node_id}"
            )

            print(
                f"  Soil Moisture    : "
                f"{packet.soil_moisture}%"
            )

            print(
                f"  Soil Temperature : "
                f"{packet.soil_temperature} °C"
            )

            print(
                f"  Canopy Humidity  : "
                f"{packet.canopy_humidity}%"
            )

            print(
                f"  Battery Level    : "
                f"{packet.battery_level}%"
            )

            print(
                f"  Frequency        : "
                f"{packet.frequency_mhz} MHz"
            )

            print(
                f"  Spreading Factor : "
                f"SF{packet.spreading_factor}"
            )

            print(
                f"  RSSI             : "
                f"{packet.rssi_dbm} dBm"
            )

            print(
                f"  SNR              : "
                f"{packet.snr_db} dB"
            )

        print("\nGateway Ingestion:")
        print(
            f"  Messages stored : "
            f"{len(gateway.get_ingested_messages())}"
        )

        print("\n[Edge Gateway] SUCCESS")

    except Exception as exc:
        print(f"[Edge Gateway Error] {exc}")


def run_voice_demo() -> None:
    """Run vernacular voice and WhatsApp simulation."""

    print_header("3. VERNACULAR VOICE PIPELINE")

    try:

        

        print("Text-to-Speech:")

        tts_result = text_to_speech(
            text="आपके खेत में मिट्टी की नमी कम है।",
            language="hi",
        )

        print(
            f"  Success  : "
            f"{tts_result.get('success')}"
        )

        print(
            f"  Language : "
            f"{tts_result.get('language')}"
        )

        print(
            f"  Voice    : "
            f"{tts_result.get('voice')}"
        )

        print(
            f"  Mode     : "
            f"{tts_result.get('mode')}"
        )

        print(
            f"  Audio    : "
            f"{tts_result.get('audio_path')}"
        )

       

        print("\nWhatsApp Webhook:")

        webhook_data = {
            "MessageSid": "SM-DEMO-001",
            "From": "whatsapp:+919999999999",
            "To": "whatsapp:+918888888888",
            "Body": "मेरे खेत की मिट्टी बहुत सूखी है।",
            "MediaUrl0": (
                "https://example.com/farmer-audio.ogg"
            ),
            "MediaContentType0": "audio/ogg",
        }

        parsed = parse_whatsapp_webhook(
            webhook_data
        )

        print(
            f"  Message SID : "
            f"{parsed.get('message_sid')}"
        )

        print(
            f"  From        : "
            f"{parsed.get('from')}"
        )

        print(
            f"  To          : "
            f"{parsed.get('to')}"
        )

        print(
            f"  Message     : "
            f"{parsed.get('message')}"
        )

        print(
            f"  Has Audio   : "
            f"{parsed.get('has_media')}"
        )

        print(
            f"  Audio Type  : "
            f"{parsed.get('media_content_type')}"
        )

       

        print("\nTwiML Response:")

        twiml = create_twiml_response(
            "आपकी किसान रिपोर्ट प्राप्त हो गई है।"
        )

        print(
            f"  {twiml}"
        )

        print("\n[Vernacular Voice] SUCCESS")

    except Exception as exc:
        print(
            f"[Vernacular Voice Error] {exc}"
        )


def main() -> None:
    """Run complete Member 3 simulation."""

    print("\n" + "*" * 70)
    print("           AGRISENTRY - MEMBER 3 SIMULATION")
    print("*" * 70)

    print(
        "\nVirtual Telemetry + "
        "Edge Gateway + "
        "Vernacular Voice Pipeline"
    )

    run_virtual_sensing_demo()

    run_edge_gateway_demo()

    run_voice_demo()

    print_header(
        "MEMBER 3 SIMULATION COMPLETED"
    )


if __name__ == "__main__":
    main()