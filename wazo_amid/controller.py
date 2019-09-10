# Copyright 2012-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from threading import Thread
from wazo_amid.ami.client import AMIClient
from wazo_amid.bus.client import BusClient
from wazo_amid import rest_api
from wazo_amid.facade import EventHandlerFacade

logger = logging.getLogger(__name__)


class Controller:

    def __init__(self, config):
        self._config = config

    def run(self):
        if self._config['publish_ami_events']:
            ami_client = AMIClient(**self._config['ami'])
            bus_client = BusClient(self._config)
            facade = EventHandlerFacade(ami_client, bus_client)
            ami_thread = Thread(target=facade.run, name='ami_thread')
            ami_thread.start()
            try:
                self._run_rest_api()
            finally:
                logger.debug('stopping facade...')
                facade.stop()
                logger.debug('facade stopped.')
                logger.debug('joining ami thread...')
                ami_thread.join()
                logger.debug('ami thread joined')
        else:
            self._run_rest_api()

    def _run_rest_api(self):
        rest_api.configure(self._config)
        rest_api.run(self._config['rest_api'])

    def stop(self, reason):
        logger.warning('Stopping wazo-amid: %s', reason)
        rest_api.stop()