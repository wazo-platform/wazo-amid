import pytest
import requests

from .helpers.base import VALID_TOKEN, APIIntegrationTest


@pytest.mark.usefixtures('base')
class TestHTTPInterface(APIIntegrationTest):
    def test_that_empty_body_returns_400(self) -> None:
        port = self.asset_cls.service_port(9491, 'amid')
        url = f'http://127.0.0.1:{port}/1.0/config'

        headers = {
            'X-Auth-Token': VALID_TOKEN,
        }

        response = requests.patch(
            url,
            headers=headers,
            data='',
            verify=False,
        )
        assert response.status_code == 400

        response = requests.patch(
            url,
            headers=headers,
            data=None,
            verify=False,
        )
        assert response.status_code == 400
