import sys
from scapy.all import rdpcap, Ether
from . import conftest
from .ieee1905_utils import *
import re
import yaml
import pytest
import pytest_check as check

ETHERTYPE_1905 = 0x893A

fragment_store = {}
m1_message_store = {}
header_1905 = ""

controller_mac = conftest.controller_mac
agent_mac = conftest.agent_mac
M2_TYPE = conftest.M2_TYPE



expected_message_types = [conftest.MSG_TYPE_AP_AUTOCONFIGURATION_RENEW,
conftest.MSG_TYPE_AP_AUTOCONFIGURATION_WSC,
conftest.MSG_TYPE_AP_TOPOLOGY_QUERY,
conftest.MSG_TYPE_AP_TOPOLOGY_RESPONSE,
conftest.MSG_TYPE_AP_CAPABILITY_REPORT,
conftest.MSG_TYPE_AP_CAPABILITY_QUERY,
conftest.MSG_TYPE_1905_ACK,
conftest.MSG_TYPE_CHANNEL_PREFERENCE_QUERY,
conftest.MSG_TYPE_CHANNEL_PREFERENCE_REPORT]


#further items will populate if the key exists in the dictionary, otherwise it will be created with the default value of {"message_ids": set()}
message_count_details = {
    msg: {"message_ids": set()}
    for msg in expected_message_types
}

message_details = {}

#########################################################

def load_yaml(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)
    
def get_profile_name(profile_type):
    profile_names = {
        0x01: "Profile 1",
        0x02: "Profile 2",
        0x03: "Profile 3"
    }
    return profile_names.get(profile_type, f"Unknown profile type: 0x{profile_type:02X}")

def get_message_type_name(message_type):
    """
    Convert hex message type to human-readable string
    """
    message_names = {
        0x0000: "Topology Discovery Message",
        0x0001: "Topology Notification Message",
        0x0002: "Topology Query Message",
        0x0003: "Topology Response Message",
        0x0005: "Link Metric Query Message",
        0x0006: "Link Metric Response Message",
        0x0007: "AP Autoconfiguration Search Message",
        0x0008: "AP Autoconfiguration Response Message",
        0x0009: "AP Autoconfiguration WSC message",
        0x000A: "AP Autoconfiguration Renew Message",
        0x8000: "1905 ACK Message",
        0x8001: "AP Capability Query Message",
        0x8002: "AP Capability Report Message",
        0x8003: "Multi-AP Policy Config Request Message",
        0x8004: "Channel Preference Query Message",
        0x8005: "Channel Preference Report Message",
        0x8006: "Channel Selection Request Message",
        0x8007: "Channel Selection Response Message",
        0x8008: "Operating Channel Report Message",
        0x8009: "Client Capability Query Message",
        0x800A: "Client Capability Report Message",
        0x800B: "AP Metrics Query Message",
        0x800C: "AP Metrics Response Message",
        0x800D: "Associated STA Link Metrics Query Message",
        0x800E: "Associated STA Link Metrics Response Message",
        0x800F: "Unassociated STA Link Metrics Query Message",
        0x8010: "Unassociated STA Link Metrics Response Message",
        0x8011: "Beacon Metrics Query Message",
        0x8012: "Beacon Metrics Response Message",
        0x8013: "Combined Infrastructure Metrics Message",
        0x8014: "Client Steering Request Message",
        0x8015: "Client Steering BTM Report Message",
        0x8016: "Client Association Control Request Message",
        0x8017: "Steering Completed Message",
        0x8018: "Higher Layer Data Message",
        0x8019: "Backhaul Steering Request Message",
        0x801A: "Backhaul Steering Response Message",
        0x801B: "Channel Scan Request Message ",
        0x801C: "Channel Scan Report Message",
        0x801D: "DPP CCE Indication Message",
        0x801E: "1905 Rekey Request Message",
        0x801F: "1905 Decryption Failure Message",
        0x8020: "CAC Request Message",
        0x8021: "CAC Termination Message",
        0x8022: "Client Disassociation Stats Message",
        0x8023: "Service Prioritization Request Message",
        0x8024: "Error Response Message",
        0x8025: "Association Status Notification Message",
        0x8026: "Tunneled Message",
        0x8027: "Backhaul STA Capability Query Message",
        0x8028: "Backhaul STA Capability Report Message",
        0x8029: "Proxied Encap DPP Message",
        0x802A: "Direct Encap DPP Message",
        0x802B: "Reconfiguration Trigger Message",
        0x802C: "BSS Configuration Request Message",
        0x802D: "BSS Configuration Response Message",
        0x802E: "BSS Configuration Result Message",
        0x802F: "Chirp Notification Message",
        0x8030: "1905 Encap EAPOL Message",
        0x8031: "DPP Bootstrapping URI Notification Message",
        0x8032: "Anticipated Channel Preference Message",
        0x8033: "Failed Connection Message",
        0x8035: "Agent List Message",
        0x8036: "Anticipated Channel Usage Report Message",
        0x8037: "QoS Management Notification Message",
        0x8038: "Virtual BSS Capabilities Request Message",
        0x8039: "Virtual BSS Capabilities Response Message",
        0x803A: "Virtual BSS Request Message",
        0x803B: "Virtual BSS Response Message",
        0x803C: "Client Security Context Request Message",
        0x803D: "Client Security Context Response Message",
        0x803E: "Trigger Channel Switch Announcement Request Message",
        0x803F: "Trigger Channel Switch Announcement Response Message",
        0x8040: "Virtual BSS Move Preparation Request Message",
        0x8041: "Virtual BSS Move Preparation Response Message",
        0x8042: "Virtual BSS Move Cancel Request Message",
        0x8043: "Early AP Capability Report Message",
        0x8044: "AP MLD Configuration Request Message",
        0x8045: "AP MLD Configuration Response Message",
        0x8046: "bSTA MLD Configuration Request Message",
        0x8047: "bSTA MLD Configuration Response Message",
        0x8048: "Virtual BSS Move Cancel Response Message",
        0x8049: "Available Spectrum Inquiry Message",
        0x804A: "Operating Channel Change Notification Message",
        0x804B: "Operating Channel Query Message",
        0x804C: "BSS Configuration Extended Request Message",
        0x804D: "BSS Configuration Extended Report Message"
    }
    return message_names.get(message_type, f"Unknown message type: 0x{message_type:04X}")


def get_tlv_type_name(tlv_type):
    """
    Convert hex TLV type to human-readable string
    """
    tlv_names = {
        0x00: "End OF Message TLV",
        0x01: "AL MAC Address TLV",
        0x02: "MAC Address TLV",
        0x03: "Device Information TLV",
        0x04: "Device Bridging Capability TLV",
        0x06: "Non-1905 neighbor device list TLV",
        0x07: "1905.1 neighbor device list TLV",
        0x08: "Link Metric Query TLV",
        0x09: "Transmitter Link Metric TLV",
        0x0A: "Receiver Link Metric TLV",
        0x0D: "Searched Role TLV",
        0x0E: "Autoconfig Frequency Band TLV",
        0x0F: "Supported Role TLV",
        0x10: "Supported Frequency Band TLV",
        0x11: "WSC TLV",
        0x80: "SupportedService TLV",
        0x81: "SearchedService TLV",
        0x82: "AP Radio Identifier TLV",
        0x83: "AP Operational BSS TLV",
        0x84: "Associated Clients TLV",
        0x85: "AP Radio Basic Capabilities TLV",
        0x86: "AP HT Capabilities TLV",
        0x87: "AP VHT Capabilities TLV",
        0x88: "AP HE Capabilities TLV",
        0x89: "Steering Policy TLV",
        0x8A: "Metric Reporting Policy TLV",
        0x8B: "Channel Preference TLV",
        0x8C: "Radio Operation Restriction TLV",
        0x8D: "Transmit Power Limit TLV",
        0x8E: "Channel Selection Response TLV",
        0x8F: "Operating Channel Report TLV",
        0x90: "Client Info TLV",
        0x91: "Client Capability Report TLV",
        0x92: "Client Association Event TLV",
        0xA0: "Higher Layer Data TLV",
        0xA1: "AP Capability TLV",
        0xA3: "Error Code TLV",
        0xA4: "Channel Scan Reporting Policy TLV",
        0xA5: "Channel Scan Capabilities TLV",
        0xA6: "Channel Scan Request TLV",
        0xA7: "Channel Scan Result TLV",
        0xA8: "Time Stamp TLV",
        0xA9: "1905 Layer Security Capability TLV",
        0xAA: "AP Wi-Fi 6 Capabilities TLV",
        0xAD: "CAC Request TLV",
        0xAE: "CAC Termination TLV",
        0xAF: "CAC Completion Report TLV",
        0xB1: "CAC Status Report TLV",
        0xB2: "CAC Capabilities TLV",
        0xB3: "Multi-AP Profile TLV",
        0xB4: "Profile 2 AP Capability TLV",
        0xB5: "Default 802.1Q Settings TLV",
        0xB6: "Traffic Separation Policy TLV",
        0xB8: "BSSID TLV",
        0xB9: "Service Prioritization Rule TLV",
        0xBA: "DSCP Mapping Table TLV",
        0xBB: "BSS Configuration Request TLV",
        0xBD: "BSS Configuration Response TLV",
        0xB7: "BSS Configuration Report TLV",
        0xBC: "Profile-2 Error Code TLV",
        0xBF: "Association Status Notification TLV",
        0xBE: "AP Radio Advanced Capabilities TLV",
        0xC0: "Source Info TLV",
        0xC1: "Tunneled message type TLV",
        0xC2: "Tunneled TLV",
        0xC4: "Unsuccessful Association Policy TLV",
        0x93: "AP Metrics Query TLV",
        0x94: "AP Metrics TLV",
        0x95: "STA MAC Address Type TLV",
        0x96: "Associated STA Link Metrics TLV",
        0x97: "Unassociated STA Link Metrics Query TLV",
        0x98: "Unassociated STA Link Metrics Response TLV",
        0x99: "Beacon Metrics Query TLV",
        0x9A: "Beacon Metrics Response TLV",
        0x9B: "Steering Request TLV",
        0x9C: "Steering BTM Report TLV",
        0x9D: "Client Association Control Request TLV",
        0x9E: "Backhaul Steering Request TLV",
        0x9F: "Backhaul Steering Response TLV",
        0xC8: "Associated STA Extended Link Metrics TLV",
        0xC3: "Profile-2 Steering Request TLV",
        0xA2: "Associated STA Traffic Stats TLV",
        0xB0: "Associated Wi-Fi 6 STA Status Report TLV",
        0xC6: "Radio Metrics TLV",
        0xC7: "AP Extended Metrics TLV",
        0xC9: "Status Code TLV",
        0xC5: "Metric Collection Interval TLV",
        0xCA: "Reason Code TLV",
        0xCB: "Backhaul STA Radio Capabilities TLV",
        0xCD: "1905 Encap DPP TLV",
        0xCE: "1905 Encap EAPOL TLV",
        0xCF: "DPP Bootstrapping URI Notification TLV",
        0xCC: "AKM Suite Capabilities TLV",
        0xD0: "Backhaul BSS Configuration TLV",
        0xD1: "DPP Message TLV",
        0xD2: "DPP CCE Indication TLV",
        0xD3: "DPP Chirp Value TLV",
        0xD5: "Agent List TLV",
        0xD6: "Anticipated Channel Preference TLV",
        0xD7: "Anticipated Channel Usage TLV",
        0xD4: "Device Inventory TLV",
        0xD8: "Spatial Reuse Request TLV",
        0xD9: "Spatial Reuse Report TLV",
        0xDA: "Spatial Reuse Config Response TLV",
        0xDB: "QoS Management Policy TLV",
        0xDC: "QoS Management Descriptor TLV",
        0xDD: "Controller Capability TLV",
        0xDE: "AP Radio VBSS Capabilities TLV",
        0xDF: "Wi-Fi 7 Agent Capabilities TLV",
        0xE0: "Agent AP MLD Configuration TLV",
        0xE1: "Backhaul STA MLD Configuration TLV",
        0xE2: "Associated STA MLD Configuration TLV",
        0xE3: "MLD Structure TLV",
        0xE4: "Affiliated STA Metrics TLV",
        0xE5: "Affiliated AP Metrics TLV",
        0xE6: "TID-to-Link Mapping Policy TLV",
        0xE7: "EHT Operations TLV",
        0xE8: "Available Spectrum Inquiry Request TLV",
        0xE9: "Available Spectrum Inquiry Response TLV",
        0xEA: "RSN Diagnostic Report TLV",
        0xEB: "RSN Parameters Configuration TLV",
        0xEC: "BSS Advanced Configuration TLV",
        0xED: "Supported Cipher Suites TLV"
    }
    return tlv_names.get(tlv_type, f"Unknown TLV type: 0x{tlv_type:02X}")


# ---------------------------------------------------------
# TLV length validation
# ---------------------------------------------------------

def validate_tlv_length(tlv_type, tlv_length):
    """
    Validate TLV length based on spec.

    Returns:
        Tuple of (expected_length: str, is_valid: bool)
    """
    if tlv_type == TLV_TYPE_AL_MAC_ADDRESS:
        return ("6", tlv_length == 6)

    if tlv_type == TLV_TYPE_MAC_ADDRESS:
        return ("6", tlv_length == 6)

    if tlv_type == TLV_TYPE_LINK_METRIC_QUERY:
        return ("8", tlv_length == 8)

    if tlv_type == TLV_TYPE_TX_LINK_METRIC:
        return ("41 or more", tlv_length >= 41)

    if tlv_type == TLV_TYPE_RX_LINK_METRIC:
        return ("35 or more", tlv_length >= 35)

    if tlv_type == TLV_TYPE_SEARCHED_ROLE:
        return ("1", tlv_length == 1)

    if tlv_type == TLV_TYPE_AUTOCONFIG_FREQ_BAND:
        return ("1", tlv_length == 1)

    if tlv_type == TLV_TYPE_SUPPORTED_ROLE:
        return ("1", tlv_length == 1)

    if tlv_type == TLV_TYPE_SUPPORTED_FREQ_BAND:
        return ("1", tlv_length == 1)

    if tlv_type == TLV_TYPE_MULTI_AP_PROFILE:
        return ("1", tlv_length == 1)

    if tlv_type == TLV_TYPE_DEVICE_INFORMATION:
        return ("1 or more", tlv_length >= 1)

    if tlv_type == TLV_TYPE_AP_OPERATIONAL_BSS:
        return ("1 or more", tlv_length >= 1)

    if tlv_type == TLV_TYPE_BSS_CONFIG_REPORT:
        return ("1 or more", tlv_length >= 1)

    if tlv_type == TLV_TYPE_WSC:
        return ("1 or more", tlv_length >= 1)

    if tlv_type == TLV_TYPE_AP_RADIO_BASIC_CAPABILITIES:
        return ("1 or more", tlv_length >= 1)

    if tlv_type == TLV_TYPE_PROFILE_2_AP_CAPABILITY:
        return ("1 or more", tlv_length >= 1)

    if tlv_type == TLV_TYPE_AP_RADIO_ADVANCED_CAPABILITIES:
        return ("1 or more", tlv_length >= 1)

    if tlv_type == TLV_TYPE_AP_RADIO_IDENTIFIER:
        return ("6", tlv_length == 6)

    if tlv_type == TLV_TYPE_END_OF_TLV:
        return ("0", tlv_length == 0)
    
    if tlv_type == TLV_TYPE_AP_CAPABILITY:
        return ("1", tlv_length == 1)
    
    if tlv_type == TLV_TYPE_CHANNEL_SCAN_CAPABILITIES:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_CHANNEL_SCAN_REQUEST:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_CAC_REQUEST:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_CAC_TERMINATION:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_CHANNEL_SCAN_RESULT:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_TIMESTAMP:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_MLD_STRUCTURE:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_CAC_CAPABILITIES:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_METRIC_COLLECTION_INTERVAL:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_1905_LAYER_SECURITY_CAPABILITY:
        return ("3", tlv_length == 3)
    
    if tlv_type == TLV_TYPE_DEVICE_INVENTORY:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_AP_HT_CAPABILITIES:
        return ("7", tlv_length == 7)

    if tlv_type == TLV_TYPE_AP_VHT_CAPABILITIES:
        return ("12", tlv_length == 12)
    
    if tlv_type == TLV_TYPE_AP_HE_CAPABILITIES:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_AP_WIFI_6_CAPABILITIES:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_SUPPORTED_SERVICE:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_BACKHAUL_STA_RADIO_CAPABILITIES:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_DEFAULT_802_1Q_SETTINGS:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_TRAFFIC_SEPARATION_POLICY:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_STEERING_POLICY:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_METRIC_REPORTING_POLICY:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_CHANNEL_SCAN_REPORTING_POLICY:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_UNSUCCESSFUL_ASSOCIATION_POLICY:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_BACKHAUL_BSS_CONFIGURATION:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_DPP_CCE_INDICATION:
        return ("1", tlv_length == 1)
    
    if tlv_type == TLV_TYPE_QOS_MANAGEMENT_POLICY:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_ERROR_CODE:
        return ("7", tlv_length == 7)

    if tlv_type == TLV_TYPE_CHANNEL_PREFERENCE:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_RADIO_OPERATION_RESTRICTION:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_CAC_COMPLETION_REPORT:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_CAC_STATUS_REPORT:
        return ("greater than 0", tlv_length > 0)
    
    if tlv_type == TLV_TYPE_CHANNEL_SELECTION_RESPONSE:
        return ("7", tlv_length == 7)

    if tlv_type == TLV_TYPE_OPERATING_CHANNEL:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_CLIENT_INFO:
        return ("12", tlv_length == 12)

    if tlv_type == TLV_TYPE_CLIENT_CAPABILITY_REPORT:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_CLIENT_ASSOCIATION_EVENT:
        return ("13", tlv_length == 13)

    if tlv_type == TLV_TYPE_REASON_CODE:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_AP_METRICS_QUERY:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_AP_METRICS:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_STA_MAC_ADDRESS_TYPE:
        return ("6", tlv_length == 6)

    if tlv_type == TLV_TYPE_RADIO_METRICS:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_AP_EXTENDED_METRICS:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_ASSOCIATED_STA_TRAFFIC_STATS:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_ASSOCIATED_STA_LINK_METRICS:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_UNASSOCIATED_STA_LINK_METRICS_QUERY:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_UNASSOCIATED_STA_LINK_METRICS_RESPONSE:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_BEACON_METRICS_QUERY:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_BEACON_METRICS_RESPONSE:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_STEERING_REQUEST:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_STEERING_BTM_REPORT:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_CLIENT_ASSOCIATION_CONTROL_REQUEST:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_BACKHAUL_STEERING_REQUEST:
        return ("14", tlv_length == 14)

    if tlv_type == TLV_TYPE_BACKHAUL_STEERING_RESPONSE:
        return ("13", tlv_length == 13)

    if tlv_type == TLV_TYPE_HIGHER_LAYER_DATA:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_PROFILE_2_STEERING_REQUEST:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_ASSOCIATED_STA_EXTENDED_LINK_METRICS:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_ASSOCIATED_WIFI_6_STA_STATUS_REPORT:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_AFFILIATED_STA_METRICS:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_AFFILIATED_AP_METRICS:
        return ("greater than 0", tlv_length > 0)
    if tlv_type == TLV_TYPE_DEVICE_BRIDGING_CAPABILITY:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_NON_1905_NEIGHBOR_DEVICE_LIST:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_1905_NEIGHBOR_DEVICE_LIST:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_SEARCHED_SERVICE:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_ASSOCIATED_CLIENTS:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_TRANSMIT_POWER_LIMIT:
        return ("7", tlv_length == 7)

    if tlv_type == TLV_TYPE_BSSID:
        return ("6", tlv_length == 6)

    if tlv_type == TLV_TYPE_PROFILE_2_ERROR_CODE:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_ASSOCIATION_STATUS_NOTIFICATION:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_SOURCE_INFO:
        return ("6", tlv_length == 6)

    if tlv_type == TLV_TYPE_STATUS_CODE:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_TUNNELED_MESSAGE_TYPE:
        return ("1", tlv_length == 1)

    if tlv_type == TLV_TYPE_TUNNELED:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_SERVICE_PRIORITIZATION_RULE:
        return ("8", tlv_length == 8)

    if tlv_type == TLV_TYPE_DSCP_MAPPING_TABLE:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_BSS_CONFIGURATION_REQUEST:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_BSS_CONFIGURATION_RESPONSE:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_BSS_CONFIGURATION_REPORT:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_QOS_MANAGEMENT_DESCRIPTOR:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_1905_ENCAP_DPP:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_1905_ENCAP_EAPOL:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_DPP_BOOTSTRAPPING_URI_NOTIFICATION:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_AGENT_LIST:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_ANTICIPATED_CHANNEL_PREFERENCE:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_ANTICIPATED_CHANNEL_USAGE:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_RSN_DIAGNOSTIC_REPORT:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_DPP_MESSAGE:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_DPP_CHIRP_VALUE:
        return ("1", tlv_length == 1)

    if tlv_type == TLV_TYPE_CONTROLLER_CAPABILITY:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_AP_RADIO_VBSS_CAPABILITIES:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_AKM_SUITE_CAPABILITIES:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_SPATIAL_REUSE_CONFIG_RESPONSE:
        return ("7", tlv_length == 7)

    if tlv_type == TLV_TYPE_SPATIAL_REUSE_REQUEST:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_SPATIAL_REUSE_REPORT:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_WIFI_7_AGENT_CAPABILITIES:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_AGENT_AP_MLD_CONFIGURATION:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_BACKHAUL_STA_MLD_CONFIGURATION:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_ASSOCIATED_STA_MLD_CONFIGURATION:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_TID_TO_LINK_MAPPING_POLICY:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_EHT_OPERATIONS:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_AVAILABLE_SPECTRUM_INQUIRY_REQUEST:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_AVAILABLE_SPECTRUM_INQUIRY_RESPONSE:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_RSN_PARAMETERS_CONFIGURATION:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_BSS_ADVANCED_CONFIGURATION:
        return ("greater than 0", tlv_length > 0)

    if tlv_type == TLV_TYPE_SUPPORTED_CIPHER_SUITES:
        return ("greater than 0", tlv_length > 0)
    
    return ("unknown", True)






