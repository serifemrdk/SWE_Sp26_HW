import unittest
from app import create_app
from app.main.utils import build_query, parse_response
import datetime


class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        return self.json_data


class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_build_query(self):
        satellite_id = "000000"
        (query, headers) = build_query(satellite_id)
        self.assertEqual(query, "https://tle.ivanstanojevic.me/api/tle/000000")

    def test_parse_response_success(self):
        response = MockResponse(200, {
            "satelliteId": 25544,
            "name": "ISS (ZARYA)",
            "date": "2026-06-07T21:37:51+00:00",
            "line1": "line1-test",
            "line2": "line2-test"
        })

        result = parse_response(response)

        self.assertEqual(result["satellite_id"], 25544)
        self.assertEqual(result["satellite_name"], "ISS (ZARYA)")
        self.assertEqual(result["date_time"], "2026-06-07T21:37:51+00:00")
        self.assertEqual(result["line1"], "line1-test")
        self.assertEqual(result["line2"], "line2-test")
        self.assertEqual(result["msg"], "OK")

    def test_parse_response_error(self):
        response = MockResponse(404, {
            "response": {
                "message": "Unable to find record"
            }
        })

        result = parse_response(response)

        self.assertIsNone(result)