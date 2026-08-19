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

# Packet Analyzer Usage

## Import Required Modules

```python
from Latest_Packet_Analyzer.packet_dissector import *
from Latest_Packet_Analyzer.conftest import *
from Latest_Packet_Analyzer.message_verify import *
from Latest_Packet_Analyzer.ieee1905_utils import *
```

## Reassemble Packets

```python
reassembled_packets = reassemble_packets("path/to/pcap/file.pcap")
```

Reassembles IEEE 1905.1 packets from the specified PCAP file and returns a list of reassembled packets.

### Parameters

- `pcap_file` : Path to the PCAP file.

### Returns

- A list of reassembled packets.

---

## Verify Message Presence

```python
payloads = check_message_presence(
    reassembled_packet,
    message_type,
    src_mac=None,
    dst_mac=None
)
```

Checks whether a specific IEEE 1905.1 message type is present in the reassembled packets.

### Parameters

- `reassembled_packet` : Output returned by `reassemble_packets()`.
- `message_type` : Message type to verify.
- `src_mac` *(Optional)* : Source MAC address used for filtering.
- `dst_mac` *(Optional)* : Destination MAC address used for filtering.

### Filtering Options

You may use:

- Both `src_mac` and `dst_mac`
- Only `src_mac`
- Only `dst_mac`
- Neither parameter

Message filtering is performed based on the provided MAC address(es).

### Returns

- A list containing payloads of all matching messages.
- Returns `None` if no matching messages are found.

---

## Verify TLV Presence

```python
tlvs = check_tlv_presence(payload, tlv_type)
```

Checks whether a specific TLV is present in a message payload.

### Parameters

- `payload` : An item from the list returned by `check_message_presence()`.
- `tlv_type` : TLV type to verify.

### Returns

- A list containing all matching TLVs.
- Returns `None` if the specified TLV is not present.

---

## Example

```python
from Latest_Packet_Analyzer.packet_dissector import *
from Latest_Packet_Analyzer.conftest import *
from Latest_Packet_Analyzer.message_verify import *
from Latest_Packet_Analyzer.ieee1905_utils import *

# Reassemble packets from a PCAP file
reassembled_packets = reassemble_packets("capture.pcap")

# Verify the presence of a specific message
payloads = check_message_presence(
    reassembled_packets,
    TOPOLOGY_RESPONSE_MESSAGE,
    src_mac="AA:BB:CC:DD:EE:FF",
    dst_mac="11:22:33:44:55:66"
)

if payloads:
    for payload in payloads:

        # Verify the presence of a TLV
        tlvs = check_tlv_presence(
            payload,
            TLV_AP_OPERATIONAL_BSS
        )

        if tlvs:
            print("TLV found")
        else:
            print("TLV not found")
else:
    print("Message not found")
```

## Typical Workflow

1. Reassemble packets from the PCAP file using `reassemble_packets()`.
2. Filter and verify the required message type using `check_message_presence()`.
3. Extract the payload returned by the message verification API.
4. Verify the required TLV using `check_tlv_presence()`.


> **Note:** For a complete working example demonstrating packet reassembly, message verification, and TLV verification, refer to:
>
> `test/ref_test/test_ssid_config_packet_analyzer_usage.py`

