# Packet Analyzer Usage Guide

This packet analyzer filters and analyzes messages exchanged between an EasyMesh Controller and a specific Extender (Agent).

## Configuration

Before running the packet analyzer, update the MAC address fields in `conftest.py`:

- Set the Controller AL-MAC address in the `controller_mac` variable.
- Set the Extender (Agent) AL-MAC address in the `agent_mac` variable.

Example `conftest.py` snippet:

```python
controller_mac = "AA:BB:CC:DD:EE:FF"
agent_mac = "11:22:33:44:55:66"
```

## Using the Packet Analyzer

Import the analyzer and call it with the path to your PCAP file. For example, from a test or small script:

```python
from Latest_Packet_Analyzer.test_logic import packet_analyzer

packet_analyzer("path/to/pcap/file.pcap")
```

Notes

- Ensure the MAC addresses in `conftest.py` match the Controller and Extender present in the capture.
- The analyzer processes only messages exchanged between the configured Controller and Extender.
- Replace `path/to/pcap/file.pcap` with the actual path to your PCAP file.