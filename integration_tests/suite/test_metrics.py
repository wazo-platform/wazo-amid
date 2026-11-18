# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import requests
from hamcrest import assert_that, contains_string, equal_to

from .helpers.base import APIIntegrationTest


@pytest.mark.usefixtures('base')
class TestMetrics(APIIntegrationTest):
    def test_metrics_without_token(self) -> None:
        self.amid.status()
        port = self.asset_cls.service_port(9491, 'amid')

        response = requests.get(f'http://127.0.0.1:{port}/1.0/metrics')

        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.text,
            contains_string('flask_http_request_total{method="GET",status="200"}'),
        )
        assert_that(
            response.text,
            contains_string(
                'flask_http_request_duration_seconds_count'
                '{endpoint="statusresource",method="GET",status="200"}'
            ),
        )
