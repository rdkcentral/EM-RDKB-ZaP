# CPU usage baseline values for stability analysis.
AVG_CPU_BASELINE = 5
# Maximum CPU usage baseline for stability analysis.
MAX_CPU_BASELINE = 20
# Time to wait after SSID update, in seconds.
SSID_UPDATE_WAITING_TIME = 100
# Time to wait after channel update, in seconds.
CHANNEL_UPDATE_WAITING_TIME = 100  
# Time to wait after fronthaul toggle, in seconds.
FRONTHAUL_TOGGLE_WAITING_TIME = 100

# Maximum number of attempts to enable fronthaul.
MAX_FRONTHAUL_ENABLE_RETRIES = 10
LOG_PATHS = ["/tmp/onewifi_em_ctrl_monitor.csv", "/tmp/onewifi_em_agent_monitor.csv", "/tmp/OneWifi_monitor.csv"]