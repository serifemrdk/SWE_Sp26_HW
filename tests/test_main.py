import unittest
from app import create_app
from unittest import mock
import datetime


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self.json_data = json_data

        def json(self):
            return self.json_data

    if args[0] == "https://tle.ivanstanojevic.me/api/tle/25544":
        tmp_response = {
            "@context": "https:\\/\\/www.w3.org\\/ns\\/hydra\\/context.jsonld",
            "@id": "https:\\/\\/tle.ivanstanojevic.me\\/api\\/tle\\/25544",
            "@type": "Tle",
            "satelliteId": 25544,
            "name": "ISS (ZARYA)",
            "date": "2026-06-07T21:37:51+00:00",
            "line1": "1 25544U 98067A   26158.90128687  .00007994  00000+0  14961-3 0  9995",
            "line2": "2 25544  51.6338 346.0598 0006926 145.2709 214.8733 15.49660544570312"
        }
        return MockResponse(200, tmp_response)

    return MockResponse(404, None)


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    @mock.patch('app.main.views.requests.get', side_effect=mocked_requests_get)
    def test_calculate_get(self, mock_get):
        response = self.client.get('/calculate')
        self.assertEqual(response.status_code, 200)

    @mock.patch('app.main.views.requests.get', side_effect=mocked_requests_get)
    def test_calculate_success(self, mock_get):
        response = self.client.post('/calculate', data={
            'input_date_time': datetime.datetime(2026, 6, 1, 12, 0)
        })
        response_text = response.get_data(as_text=True)

        self.assertIn("TLE DateTime: 2026-06-07T21:37:51+00:00", response_text)
        self.assertIn("Position (X, Y, Z) in km:", response_text)
        self.assertIn("Velocity (dx, dy, dz) in km/s:", response_text)

    @mock.patch('app.main.views.parse_satellite')
    @mock.patch('app.main.views.requests.get', side_effect=mocked_requests_get)
    def test_calculate_satellite_error(self, mock_get, mock_parse_satellite):
        mock_parse_satellite.return_value = (1, None, None)

        response = self.client.post('/calculate', data={
            'input_date_time': datetime.datetime(2026, 6, 1, 12, 0)
        })

        self.assertIn("Something went wrong. Try again.", response.get_data(as_text=True))

    @mock.patch('app.main.views.parse_response')
    @mock.patch('app.main.views.requests.get', side_effect=mocked_requests_get)
    def test_calculate_api_error(self, mock_get, mock_parse_response):
        mock_parse_response.return_value = None

        response = self.client.post('/calculate', data={
            'input_date_time': datetime.datetime(2026, 6, 1, 12, 0)
        })

        self.assertIn("Something went wrong. Try again.", response.get_data(as_text=True))

    def test_mock_404(self):
        response = mocked_requests_get(
            "https://tle.ivanstanojevic.me/api/tle/999999"
        )

        self.assertEqual(response.status_code, 404)