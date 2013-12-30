# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

import argparse
import collections
from contextlib import contextmanager
import logging
import signal
import time

from xivo import daemonize
from xivo_ami.ami.client import AMIClient, AMIConnectionError

_LOG_FILENAME = '/var/log/xivo-amid.log'
_PID_FILENAME = '/var/run/xivo-amid.pid'
_RECON_DELAY = 5

logger = logging.getLogger(__name__)


def main():
    parsed_args = _parse_args()

    _init_logging(parsed_args)

    if not parsed_args.foreground:
        daemonize.daemonize()

    logger.info('Starting xivo-amid')
    daemonize.lock_pidfile_or_die(_PID_FILENAME)
    try:
        _run()
    except Exception:
        logger.exception('Unexpected error:')
    finally:
        logger.info('Stopping xivo-amid')
        daemonize.unlock_pidfile(_PID_FILENAME)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--foreground', action='store_true',
                        help='run in foreground')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase verbosity')
    return parser.parse_args()


def _init_logging(parsed_args):
    level = logging.DEBUG if parsed_args.verbose else logging.INFO
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    if parsed_args.foreground:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s (%(levelname)s): %(message)s'))
    else:
        handler = logging.FileHandler(_LOG_FILENAME)
        handler.setFormatter(logging.Formatter('%(asctime)s [%(process)d] (%(levelname)s): %(message)s'))
    root_logger.addHandler(handler)


def _run():
    message_queue = collections.deque()
    _init_signal()
    with _new_ami_client() as ami_client:
        while True:
            try:
                ami_client.connect_and_login()
                while True:
                    ami_client.parse_next_messages(message_queue)
                    _process_messages(message_queue)
            except AMIConnectionError as e:
                logger.debug('AMIConnectionError %s. Reconnecting', e)
                ami_client.disconnect()
                time.sleep(_RECON_DELAY)


def _init_signal():
    signal.signal(signal.SIGTERM, _handle_sigterm)


def _handle_sigterm(signum, frame):
    raise SystemExit()


def _process_messages(message_queue):
    while message_queue:
        msg = message_queue.popleft()
        logger.debug('Processing message %s', msg)


@contextmanager
def _new_ami_client():
    ami_client = AMIClient('localhost', 'xivo_amid', 'eeCho8ied3u')
    try:
        yield ami_client
    finally:
        ami_client.disconnect()


if __name__ == '__main__':
    main()
