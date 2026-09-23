# Shared stability test configuration values.
# Timeout for the 24-hour stability loop, expressed in seconds. [test_stability_24hours]
timeout = 24 * 60 * 60  # 24 hours expressed in seconds
# Number of SSID update iterations to run in the SSID stability test. [test_stability_ssid_update]
ssid_update_max_count = 100

# Number of fronthaul toggle iterations to run in the fronthaul stability test. [test_stability_fronthaul_toggle]
fronthaul_toggle_max_count = 100

# Number of channel update iterations to run in the channel stability test. [test_stability_channel_update]
channel_update_max_count = 100
