import unittest

from modules.telemetry_voice.edge_gateway_sim import (
    FarmSensorNode,
    VillageGateway,
    InMemoryMessageBus,
    SensorTelemetry,
    SerialTelemetry,
    calculate_checksum,
    encode_serial_frame,
    decode_serial_frame,
    create_default_gateway,
)


class TestEdgeGateway(unittest.TestCase):

   

    def test_sensor_generates_telemetry(self):

        node = FarmSensorNode(
            "FARM-NODE-01"
        )

        telemetry = node.generate_telemetry()

        self.assertIsInstance(
            telemetry,
            SensorTelemetry
        )

        self.assertEqual(
            telemetry.node_id,
            "FARM-NODE-01"
        )

        self.assertTrue(
            15.0 <= telemetry.soil_moisture <= 45.0
        )

        self.assertTrue(
            20.0 <= telemetry.soil_temperature <= 35.0
        )

        self.assertTrue(
            50.0 <= telemetry.battery_level <= 100.0
        )

   

    def test_lorawan_metadata(self):

        node = FarmSensorNode(
            "FARM-NODE-01"
        )

        telemetry = node.generate_telemetry()

        self.assertTrue(
            865 <= telemetry.frequency_mhz <= 867
        )

        self.assertIn(
            telemetry.spreading_factor,
            [7, 8, 9, 10, 11, 12]
        )

        self.assertTrue(
            -115 <= telemetry.rssi_dbm <= -80
        )

        self.assertTrue(
            6 <= telemetry.snr_db <= 12
        )

   

    def test_in_memory_message_bus(self):

        bus = InMemoryMessageBus()

        received = []

        def subscriber(message):
            received.append(message)

        bus.subscribe(subscriber)

        payload = {
            "node_id": "FARM-NODE-01",
            "soil_moisture": 25.5,
        }

        bus.publish(
            "agrisentry/telemetry",
            payload,
        )

        messages = bus.get_messages()

        self.assertEqual(
            len(messages),
            1
        )

        self.assertEqual(
            messages[0]["topic"],
            "agrisentry/telemetry"
        )

        self.assertEqual(
            messages[0]["payload"],
            payload
        )

        self.assertEqual(
            len(received),
            1
        )

   
    def test_gateway_has_nodes(self):

        gateway = create_default_gateway()

        self.assertEqual(
            len(gateway.nodes),
            3
        )

        node_ids = [
            node.node_id
            for node in gateway.nodes
        ]

        self.assertIn(
            "FARM-NODE-01",
            node_ids
        )

        self.assertIn(
            "FARM-NODE-02",
            node_ids
        )

        self.assertIn(
            "FARM-NODE-03",
            node_ids
        )

    

    def test_gateway_broadcast(self):

        gateway = create_default_gateway()

        packets = gateway.broadcast_once()

        self.assertEqual(
            len(packets),
            3
        )

        self.assertEqual(
            gateway.packets_received,
            3
        )

        messages = gateway.get_ingested_messages()

        self.assertEqual(
            len(messages),
            3
        )

   

    def test_serial_encoding(self):

        frame = encode_serial_frame(
            "NODE1",
            24.8,
            28.4,
        )

        self.assertTrue(
            frame.startswith("$AGRI,")
        )

        self.assertIn(
            "NODE1",
            frame
        )

        self.assertIn(
            "MOIST:24.8",
            frame
        )

        self.assertIn(
            "TEMP:28.4",
            frame
        )

        self.assertIn(
            "*",
            frame
        )

    
    def test_serial_decoding(self):

        frame = encode_serial_frame(
            "NODE1",
            24.8,
            28.4,
        )

        decoded = decode_serial_frame(
            frame
        )

        self.assertIsInstance(
            decoded,
            SerialTelemetry
        )

        self.assertEqual(
            decoded.node_id,
            "NODE1"
        )

        self.assertAlmostEqual(
            decoded.soil_moisture,
            24.8,
            places=1
        )

        self.assertAlmostEqual(
            decoded.soil_temperature,
            28.4,
            places=1
        )

   
    def test_checksum(self):

        body = (
            "AGRI,NODE1,"
            "MOIST:24.8,"
            "TEMP:28.4"
        )

        checksum = calculate_checksum(
            body
        )

        self.assertEqual(
            len(checksum),
            2
        )

        int(
            checksum,
            16
        )

    

    def test_invalid_serial_frame(self):

        invalid_frame = (
            "$AGRI,NODE1,"
            "MOIST:24.8,"
            "TEMP:28.4*00"
        )

        with self.assertRaises(
            ValueError
        ):
            decode_serial_frame(
                invalid_frame
            )


if __name__ == "__main__":
    unittest.main()