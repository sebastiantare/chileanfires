import unittest
from app import create_app

class TestAPIRoutes(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config.update({
            "TESTING": True,
            'PARQUET_FILE_PATH': 'tests/test.parquet' # Subset of 100 samples
            #'PARQUET_FILE_PATH': 'db/fires.parquet'
        })
        self.app = app
        self.client = app.test_client()

    def tearDown(self):
        # clean up / reset resources here
        pass

    def test_db_data_integrity(self):
        response = self.client.get("/api/latest_fires")

        sample_json = {"acq_date":"Sat, 23 Dec 2023 00:00:00 GMT","acq_time":1806,"confidence":"n","daynight":"D","frp":6.29,"hour":18,"latitude":-32.76143,"longitude":-71.19239,"scan":0.42,"track":0.45}
        json_keys = sample_json.keys()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json[0].keys(), json_keys) # Has the default columns
        self.assertGreater(len(response.json), 1) # Returns more than 1 value

    def test_db_data_dates(self):
        import pandas as pd

        response = self.client.get("/api/latest_fires")

        df = pd.DataFrame(response.json)

        print(df.head())

        # Check if all 'acq_date' values can be converted to datetime
        df['acq_date'] = pd.to_datetime(df['acq_date'], errors='coerce')

        self.assertFalse(df['acq_date'].isnull().any(), "Invalid date format in 'acq_date'")


if __name__ == '__main__':
    unittest.main()
