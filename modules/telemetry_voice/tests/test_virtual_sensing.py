import unittest

from modules.telemetry_voice.virtual_sensing import (
    SoilTelemetryData,
    NDVIIndexData,
    classify_ndvi,
    generate_soil_fallback,
    generate_ndvi_fallback,
    get_unified_virtual_sensing,
)


class TestVirtualSensing(unittest.TestCase):

    LATITUDE = 26.8467
    LONGITUDE = 80.9462

    

    def test_ndvi_healthy(self):
        result = classify_ndvi(0.75)

        self.assertEqual(
            result,
            "Dense / Healthy Canopy"
        )

    def test_ndvi_moderate(self):
        result = classify_ndvi(0.45)

        self.assertEqual(
            result,
            "Moderate / Developing Vegetation"
        )

    def test_ndvi_stressed(self):
        result = classify_ndvi(0.20)

        self.assertEqual(
            result,
            "Stressed / Sparse Canopy or Bare Soil"
        )

   

    def test_soil_fallback(self):

        result = generate_soil_fallback(
            self.LATITUDE,
            self.LONGITUDE,
        )

        self.assertIsInstance(
            result,
            SoilTelemetryData
        )

        self.assertTrue(
            result.is_simulated
        )

        self.assertGreaterEqual(
            result.soil_moisture,
            0.0
        )

        self.assertGreaterEqual(
            result.relative_humidity,
            0.0
        )

        self.assertLessEqual(
            result.relative_humidity,
            100.0
        )

   
    def test_ndvi_fallback(self):

        result = generate_ndvi_fallback(
            self.LATITUDE,
            self.LONGITUDE,
        )

        self.assertIsInstance(
            result,
            NDVIIndexData
        )

        self.assertTrue(
            result.is_simulated
        )

        self.assertGreaterEqual(
            result.ndvi_mean,
            -1.0
        )

        self.assertLessEqual(
            result.ndvi_mean,
            1.0
        )

        self.assertGreaterEqual(
            result.cloud_cover,
            0.0
        )

        self.assertLessEqual(
            result.cloud_cover,
            100.0
        )

    
    def test_unified_virtual_sensing(self):

        result = get_unified_virtual_sensing(
            self.LATITUDE,
            self.LONGITUDE,
        )

        self.assertEqual(
            result.latitude,
            self.LATITUDE
        )

        self.assertEqual(
            result.longitude,
            self.LONGITUDE
        )

        self.assertIsInstance(
            result.soil,
            SoilTelemetryData
        )

        self.assertIsInstance(
            result.ndvi,
            NDVIIndexData
        )

        self.assertIsNotNone(
            result.generated_at
        )


if __name__ == "__main__":
    unittest.main()