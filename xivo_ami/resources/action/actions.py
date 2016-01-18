# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import json
import logging
import requests

from flask import request

from xivo_ami.ami import parser
from xivo_ami.core.exceptions import APIException
from xivo_ami.core.rest_api import AuthResource

VERSION = 1.0

logger = logging.getLogger(__name__)


class AJAMUnreachable(APIException):

    def __init__(self, ajam_url, error):
        super(AJAMUnreachable, self).__init__(
            status_code=503,
            message='AJAM server unreachable',
            error_id='ajam-unreachable',
            details={
                'ajam_url': ajam_url,
                'original_error': str(error),
            }
        )


class UnsupportedAction(APIException):

    def __init__(self, action):
        super(UnsupportedAction, self).__init__(
            status_code=501,
            message='Action incompatible with xivo-amid',
            error_id='incompatible-action',
            details={
                'action': action
            }
        )


class Actions(AuthResource):

    @classmethod
    def configure(cls, config):
        cls.ajam_url = 'https://{host}:{port}/rawman'.format(**config['ajam'])
        cls.login_params = {
            'action': 'login',
            'username': config['ajam']['username'],
            'secret': config['ajam']['password'],
        }
        cls.verify = config['ajam']['verify_certificate']

    def post(self, action):
        if action.lower() in ('queues', 'command'):
            raise UnsupportedAction(action)

        extra_args = json.loads(request.data) if request.data else {}

        with requests.Session() as session:
            try:
                session.get(self.ajam_url, params=self.login_params, verify=self.verify)

                response = session.get(self.ajam_url, params=_ajam_params(action, extra_args))
            except requests.RequestException as e:
                raise AJAMUnreachable(self.ajam_url, e)

        return _parse_ami(response.content), 200


def _ajam_params(action, ami_args):
    result = [('action', action)]
    for extra_arg_key, extra_arg_value in ami_args.iteritems():
        if isinstance(extra_arg_value, list):
            result.extend([(extra_arg_key, value) for value in extra_arg_value])
        else:
            result.append((extra_arg_key, extra_arg_value))

    return result


def _parse_ami(buffer_):
    result = []

    def aux(event_name, action_id, message):
        result.append(message)

    parser.parse_buffer(buffer_, aux, aux)

    return result