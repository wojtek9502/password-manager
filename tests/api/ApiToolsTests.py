import os
from tests.api.ApiBaseTests import ApiBaseTest


class ApiToolsTests(ApiBaseTest):
    def test_healthz(self):
        # given
        API_AUTH_TOKEN = os.environ['API_AUTH_MASTER_TOKEN']
        headers = {
            "X-API-KEY": API_AUTH_TOKEN,
            'Accept': 'application/json'
        }

        expected_response = {'status': 'ok'}

        # when
        response = self.test_api.get(
            url="/healthz",
            headers=headers
        )
        response_json = response.json()

        # then
        assert response_json == expected_response
