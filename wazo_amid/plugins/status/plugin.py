# Copyright 2023-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from xivo.status import Status

from .http import StatusResource

if TYPE_CHECKING:
    from xivo.status import StatusDict

    from wazo_amid.rest_api import PluginDependencies


class Plugin:
    def load(self, dependencies: PluginDependencies) -> None:
        api = dependencies['api']
        status_aggregator = dependencies['status_aggregator']

        status_aggregator.add_provider(provide_status)

        api.add_resource(
            StatusResource,
            '/status',
            resource_class_args=[status_aggregator],
        )


def provide_status(status: StatusDict) -> None:
    status['rest_api']['status'] = Status.ok
