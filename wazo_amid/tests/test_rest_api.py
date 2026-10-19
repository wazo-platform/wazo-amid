# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import cast
from unittest.mock import patch

import pytest

from wazo_amid import rest_api
from wazo_amid.config import RestApiConfigDict

CONFIG = cast(
    RestApiConfigDict,
    {
        'listen': '127.0.0.1',
        'port': 9491,
        'min_threads': 1,
        'max_threads': 1,
        'certificate': None,
        'private_key': None,
        'cors': {'enabled': False},
    },
)


@pytest.fixture(autouse=True)
def reset_module_state():
    # run() and stop() work on module-level state; isolate each test
    rest_api.wsgi_server = None
    rest_api._stopped.clear()


def test_stop_before_run_does_not_raise_and_sets_the_tombstone():
    rest_api.stop()

    assert rest_api._stopped.is_set()


@patch('wazo_amid.rest_api.wsgi')
def test_run_after_stop_does_not_start_the_server(wsgi):
    rest_api.stop()
    rest_api.run(CONFIG)

    wsgi.DynamicWSGIServer.return_value.start.assert_not_called()


@patch('wazo_amid.rest_api.wsgi')
def test_stop_after_run_stops_the_server(wsgi):
    rest_api.run(CONFIG)
    rest_api.stop()

    wsgi.DynamicWSGIServer.return_value.stop.assert_called_once_with()
