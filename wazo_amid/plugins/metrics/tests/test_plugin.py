# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import cast
from unittest.mock import Mock, patch

from wazo_amid.rest_api import PluginDependencies

from ..plugin import Plugin


@patch('wazo_amid.plugins.metrics.plugin.init_flask_metrics')
def test_load_instruments_the_api_app(init_flask_metrics):
    api = Mock()

    Plugin().load(cast(PluginDependencies, {'api': api}))

    init_flask_metrics.assert_called_once_with(api.app, api)
