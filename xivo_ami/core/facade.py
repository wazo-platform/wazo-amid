# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
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

import logging
import time

from xivo_ami.ami.client import AMIConnectionError

logger = logging.getLogger(__name__)


class EventHandlerFacade(object):

    RECONNECTION_DELAY = 5

    def __init__(self, ami_client, bus_client):
        self._ami_client = ami_client
        self._bus_client = bus_client
        self._should_stop = False

    def run(self):
        while not self._should_stop:
            try:
                self._ami_client.connect_and_login()
                self._process_messages_indefinitely()
            except AMIConnectionError:
                self._handle_ami_connection_error()
            except Exception as e:
                self._handle_unexpected_error(e)

    def _handle_ami_connection_error(self):
        self._ami_client.disconnect()
        if not self._should_stop:
            time.sleep(self.RECONNECTION_DELAY)

    def _handle_unexpected_error(self, e):
        self._ami_client.disconnect()
        raise

    def _process_messages_indefinitely(self):
        while not self._should_stop:
            new_messages = self._ami_client.parse_next_messages()
            self._process_messages(new_messages)

    def _process_messages(self, messages):
        while len(messages):
            message = messages.pop()
            logger.debug('Processing message %s', message)
            self._bus_client.publish(message)

    def stop(self):
        self._should_stop = True
        self._ami_client.stop()