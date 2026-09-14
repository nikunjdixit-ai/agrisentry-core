import unittest

from api.tools.agri_tools import (
    WeatherForecastInput,
    VendorCatalogInput,
    MandiPricesInput,
    get_weather_forecast,
    search_vendor_catalog,
    fetch_mandi_prices,
)


class TestAgriTools(unittest.TestCase):

    def test_weather_schema(self):
        data = WeatherForecastInput(
            location="Punjab",
            days=3
        )

        self.assertEqual(data.location, "Punjab")
        self.assertEqual(data.days, 3)

    def test_vendor_schema(self):
        data = VendorCatalogInput(
            item_type="pesticide",
            region="Punjab"
        )

        self.assertEqual(data.item_type, "pesticide")
        self.assertEqual(data.region, "Punjab")

    def test_mandi_schema(self):
        data = MandiPricesInput(
            crop="cotton",
            state="Punjab"
        )

        self.assertEqual(data.crop, "cotton")
        self.assertEqual(data.state, "Punjab")

    def test_weather_tool(self):
        result = get_weather_forecast.invoke(
            {
                "location": "Punjab",
                "days": 3
            }
        )

        self.assertIn("temperature_c", result)
        self.assertIn("humidity_percent", result)

    def test_vendor_tool(self):
        result = search_vendor_catalog.invoke(
            {
                "item_type": "pesticide",
                "region": "Punjab"
            }
        )

        self.assertTrue(len(result) > 0)
        self.assertEqual(result[0]["dealer_name"], "AgriMart")

    def test_mandi_tool(self):
        result = fetch_mandi_prices.invoke(
            {
                "crop": "cotton",
                "state": "Punjab"
            }
        )

        self.assertIn("modal_price_per_quintal", result)


if __name__ == "__main__":
    unittest.main()