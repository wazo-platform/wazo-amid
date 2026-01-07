# Copyright 2015-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import string

import pytest
import requests
from hamcrest import (
    assert_that,
    calling,
    contains,
    contains_string,
    has_entries,
    has_entry,
    has_item,
    has_properties,
    matches_regexp,
)
from wazo_amid_client.exceptions import AmidError
from wazo_test_helpers.hamcrest.raises import raises

from .helpers.base import VALID_TOKEN, APIIntegrationTest


@pytest.mark.usefixtures('base')
class TestHTTPAction(APIIntegrationTest):
    def test_that_action_ping_returns_pong(self) -> None:
        result = self.amid.action('Ping')

        assert_that(
            result,
            contains(
                has_entries(
                    {
                        'Response': 'Success',
                        'Ping': 'Pong',
                        'Timestamp': matches_regexp('.*'),
                    }
                )
            ),
        )

    def test_that_malformatted_actions_are_refused(self) -> None:
        # the format of Queues response is suited for display, not parsing
        assert_that(
            calling(self.amid.action).with_args('Queues'),
            raises(AmidError).matching(has_properties(status_code=501)),
        )

    def test_that_action_with_events_returns_events(self) -> None:
        result = self.amid.action('QueueStatus')

        assert_that(
            result,
            contains(
                has_entries(
                    {
                        'Response': 'Success',
                        'EventList': 'start',
                        'Message': 'Queue status will follow',
                    }
                ),
                has_entries(
                    {
                        'Event': 'QueueParams',
                        'Queue': 'my_queue',
                        'Max': '0',
                        'Strategy': 'ringall',
                        'Calls': '0',
                        'Holdtime': '0',
                        'TalkTime': '0',
                        'Completed': '0',
                        'Abandoned': '0',
                        'ServiceLevel': '0',
                        'ServicelevelPerf': '0.0',
                        'Weight': '0',
                    }
                ),
                has_entries(
                    {
                        'Event': 'QueueStatusComplete',
                        'EventList': 'Complete',
                        'ListItems': '1',
                    }
                ),
            ),
        )

    def test_that_action_with_parameters_sends_parameters(self) -> None:
        key = ''.join(random.choice(string.ascii_letters) for _ in range(10))

        self.amid.action('DBPut', {'Family': key, 'Key': key, 'Val': key})
        result = self.amid.action('DBGet', {'Family': key, 'Key': key})

        assert_that(
            result,
            has_item(
                has_entries(
                    {'Event': 'DBGetResponse', 'Family': key, 'Key': key, 'Val': key}
                )
            ),
        )

    def test_that_action_can_send_and_receive_non_ascii(self) -> None:
        family = 'my-family'
        key = 'my-key'
        value = 'non-ascii-value äåéëþüü'

        self.amid.action('DBPut', {'Family': family, 'Key': key, 'Val': value})
        result = self.amid.action('DBGet', {'Family': family, 'Key': key})

        assert_that(
            result,
            has_item(
                has_entries(
                    {
                        'Event': 'DBGetResponse',
                        'Family': family,
                        'Key': key,
                        'Val': value,
                    }
                )
            ),
        )


@pytest.mark.usefixtures('base')
class TestHTTPCommand(APIIntegrationTest):
    def test_given_no_command_when_action_command_then_error_400(self) -> None:
        assert_that(
            calling(self.amid.command).with_args({}),
            raises(AmidError).matching(
                has_properties(
                    status_code=400,
                    error_id='invalid-data',
                )
            ),
        )

    def test_that_action_command_returns_command_response(self) -> None:
        result = self.amid.command('moh show classes')

        assert_that(
            result,
            has_entry(
                'response',
                contains(
                    'Class: default',
                    '	Mode: files',
                    '	Directory: /var/lib/wazo/moh/default',
                ),
            ),
        )


@pytest.mark.usefixtures('base')
class TestHTTPMultipleIdenticalKeys(APIIntegrationTest):
    def test_when_action_with_multiple_identical_keys_then_all_keys_are_sent(
        self,
    ) -> None:
        self.amid.action('Originate', {'Variable': ('Var1=one', 'Var2=two')})

        assert_that(
            self.ajam_requests(),
            has_entry(
                'requests',
                has_item(
                    has_entries(
                        {
                            'method': 'GET',
                            'path': '/rawman',
                            'query': contains(
                                ['action', 'Originate'],
                                ['Variable', 'Var1=one'],
                                ['Variable', 'Var2=two'],
                            ),
                        }
                    )
                ),
            ),
        )


@pytest.mark.usefixtures('base')
class TestHTTPError(APIIntegrationTest):
    def test_given_no_ajam_when_http_request_then_status_code_503(self) -> None:
        with self.ajam_stopped():
            assert_that(
                calling(self.amid.action).with_args('ping'),
                raises(AmidError).matching(
                    has_properties(
                        status_code=503,
                        details=has_entries(
                            ajam_url=contains_string('asterisk-ajam:5039'),
                        ),
                    )
                ),
            )

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
