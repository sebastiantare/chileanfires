import unittest
from app import create_app
import pandas as pd
from time import sleep

class TestAPIRoutes(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config.update({
            "TESTING": True,
            'PARQUET_FILE_PATH': 'tests/test.parquet',  # Subset of 100 samples
            # 'PARQUET_FILE_PATH': 'db/fires.parquet'
            'REQUEST_LIMIT': '10 per minute'
        })
        self.app = app
        self.client = app.test_client()
        

    def tearDown(self):
        # clean up / reset resources here
        pass

    def test_db_data_integrity(self):
        response = self.client.get("/api/latest_fires")

        sample_json = {"acq_date": "Sat, 23 Dec 2023 00:00:00 GMT", "acq_time": 1806, "confidence": "n", "daynight": "D",
                       "frp": 6.29, "hour": 18, "latitude": -32.76143, "longitude": -71.19239, "scan": 0.42, "track": 0.45}
        json_keys = sample_json.keys()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json[0].keys(), json_keys) # Has the default columns
        self.assertGreater(len(response.json), 0)  # Returns more than 0 value

    def test_db_data_dates(self):
        response = self.client.get("/api/latest_fires")

        df = pd.DataFrame(response.json)

        # Check if all 'acq_date' values can be converted to datetime
        df['acq_date'] = pd.to_datetime(df['acq_date'], errors='coerce')
        self.assertFalse(df['acq_date'].isnull().any(), "Invalid date format in 'acq_date'")

    def test_fires_by_correct_date(self):
        # Input a correct date and expect results
        correct_date = '2023-01-01'
        response = self.client.get(f"/api/fires_by_date?date={correct_date}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        # Add more assertions based on the expected format or values in the response

    def test_fires_by_incorrect_date(self):
        # Input an incorrect date and expect an error
        incorrect_date = 'invalid_date_format'
        response = self.client.get(f"/api/fires_by_date?date={incorrect_date}")

        self.assertEqual(response.status_code, 400)
        error_message = response.json.get('error')
        self.assertIsNotNone(error_message)

if __name__ == '__main__':
    unittest.main()
