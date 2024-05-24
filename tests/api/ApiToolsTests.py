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

    def test_api_call_with_wrong_token(self):
        # given
        API_AUTH_TOKEN = 'abcd'
        headers = {
            "X-API-KEY": API_AUTH_TOKEN,
            'Accept': 'application/json'
        }

        # when
        response = self.test_api.get(
            url="/password/list",
            headers=headers
        )

        # then
        assert response.status_code == 401
        assert 'Invalid or missing API Key' == response.json()['detail']

    def test_api_call_without_token(self):
        # given
        headers = {
            'Accept': 'application/json'
        }

        # when
        response = self.test_api.get(
            url="/password/list",
            headers=headers
        )

        # then
        assert response.status_code == 401
        assert 'Invalid or missing API Key' == response.json()['detail']
