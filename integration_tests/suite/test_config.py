# Copyright 2024-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import requests
from hamcrest import assert_that, equal_to, has_entry

from .helpers.base import VALID_TOKEN, APIIntegrationTest

FAKE_EVENT = {'data': 'Event: foo\r\nAnswerToTheUniverse: 42\r\n\r\n'}

DEFAULT_RECONNECTION_DELAY = 5

VERSION = '1.0'


@pytest.mark.usefixtures('base')
class TestConfigAPI(APIIntegrationTest):
    def test_config_response(self) -> None:
        result = self.amid.config()
        assert_that(result['debug'], equal_to(True))

    def test_update_config(self) -> None:
        debug_true_config = [
            {
                'op': 'replace',
                'path': '/debug',
                'value': "True",
            }
        ]

        debug_false_config = [
            {
                'op': 'replace',
                'path': '/debug',
                'value': "False",
            }
        ]

        debug_true_patched_config = self.amid.config.patch(debug_true_config)
        debug_true_config = self.amid.config()
        assert_that(debug_true_patched_config, equal_to(debug_true_config))
        assert_that(debug_true_config, has_entry('debug', True))

        debug_false_patched_config = self.amid.config.patch(debug_false_config)
        debug_false_config = self.amid.config()
        assert_that(debug_false_patched_config, equal_to(debug_false_config))
        assert_that(debug_false_config, has_entry('debug', False))

    def _make_raw_http_call(
        self, verb: str, url: str, body: str | None
    ) -> requests.Response:
        headers = {
            'X-Auth-Token': VALID_TOKEN,
        }

        match verb:
            case 'post':
                call = requests.post
            case 'patch':
                call = requests.patch  # type: ignore
            case _:
                raise ValueError('Unexpected verb')

        return call(
            url,
            headers=headers,
            data=body,
            verify=False,
        )

    def test_that_empty_body_returns_400(self) -> None:
        port = self.asset_cls.service_port(9491, 'amid')
        urls = [
            ('patch', f'http://127.0.0.1:{port}/1.0/config'),
            ('post', f'http://127.0.0.1:{port}/1.0/action/Command'),
        ]

        for url in urls:
            response = self._make_raw_http_call(url[0], url[1], '')
            assert response.status_code == 400, f'Error with url: {url}'

            response = self._make_raw_http_call(url[0], url[1], None)
            assert response.status_code == 400, f'Error with url: {url}'
