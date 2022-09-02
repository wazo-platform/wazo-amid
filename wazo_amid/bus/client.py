# Copyright 2012-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.publisher import BusPublisherWithQueue
from xivo_bus.resources.ami.event import AMIEvent
from xivo.status import Status


class BusClient(BusPublisherWithQueue):
    @classmethod
    def from_config(cls, service_uuid, bus_config):
        name = 'wazo-amid'
        return cls(name=name, service_uuid=service_uuid, **bus_config)

    def provide_status(self, status):
        status['bus_publisher']['status'] = (
            Status.ok if self.queue_publisher_connected() else Status.fail
        )

    def publish(self, *messages):
        for message in messages:
            super().publish_soon(AMIEvent(message.name, message.headers))
