# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.status import Status

from .http import StatusResource


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        status_aggregator = dependencies['status_aggregator']

        status_aggregator.add_provider(provide_status)

        api.add_resource(
            StatusResource,
            '/status',
            resource_class_args=[status_aggregator],
        )


def provide_status(status):
    status['rest_api']['status'] = Status.ok
