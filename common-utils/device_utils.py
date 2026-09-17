"""Helpers for discovering configured testbed devices."""


def get_enabled_extenders(initialize):
    """Return extender devices enabled in the testbed configuration."""
    return [
        device
        for device in initialize.get_testbed_devices()
        if device.startswith("extender") and "_client_" not in device
    ]


def get_enabled_extender_macs(initialize):
    """Return enabled extender names mapped to their normalized AL MACs."""
    return {
        device: initialize.get_al_mac_address(device, "cli").lower()
        for device in get_enabled_extenders(initialize)
    }
