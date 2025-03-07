# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Test module for ejabberd STUN/TURN configuration.
"""

from unittest.mock import patch

from plinth.modules import ejabberd
from plinth.modules.coturn.components import TurnConfiguration

managed_configuration = TurnConfiguration(
    'freedombox.local', [],
    'aiP02OAGyOlj6WGuCyqj7iaOsbkC7BUeKvKzhAsTZ8MEwMd3yTwpr2uvbOxgWe51')

overridden_configuration = TurnConfiguration(
    'public.coturn.site', [],
    'BUeKvKzhAsTZ8MEwMd3yTwpr2uvbOxgWe51aiP02OAGyOlj6WGuCyqj7iaOsbkC7')


def _set_turn_configuration(monkeypatch, config=managed_configuration,
                            managed=True):
    monkeypatch.setattr('sys.stdin', config.to_json())
    with patch('plinth.action_utils.service_is_running', return_value=False):
        ejabberd.update_turn_configuration(config, managed=managed)


def _assert_conf(expected_configuration, expected_managed):
    """Assert that ejabberd TURN configuration is as expected."""
    config, managed = ejabberd.get_turn_configuration()
    assert config.uris == expected_configuration.uris
    assert config.shared_secret == expected_configuration.shared_secret
    assert managed == expected_managed


def test_managed_turn_server_configuration(monkeypatch):
    _set_turn_configuration(monkeypatch)
    _assert_conf(managed_configuration, True)


def test_overridden_turn_server_configuration(monkeypatch):
    _set_turn_configuration(monkeypatch, overridden_configuration, False)
    _assert_conf(overridden_configuration, False)


def test_remove_turn_configuration(monkeypatch):
    _set_turn_configuration(monkeypatch)
    _set_turn_configuration(monkeypatch, TurnConfiguration(), False)
    _assert_conf(TurnConfiguration(), False)
