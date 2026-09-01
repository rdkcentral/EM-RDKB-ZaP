# If not stated otherwise in this file or this component LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2026 Zilogic Systems
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from zaero.utils import zi_logger

# ---------------------------------------------------------------------------
# 1. Onboarding Data Elements (6)
# ---------------------------------------------------------------------------

def test_device_number_of_entries_de(initialize):
    """
    Test case for device number of entries data element.
    """
    zi_logger.print_step("Test case for device number of entries data element.")
    device_count = initialize.get_device_number_of_entries('controller')
    if device_count == 0:
        zi_logger.print_error("No devices found, skipping the test.")
    else:
        zi_logger.print_success(f"Device count: {device_count}")

def test_device_id_de(initialize):
    """
    Test case for device ID data element.
    """
    zi_logger.print_step("\n Test case for device ID data element.")
    controller_device_index = initialize.read_from_database("controller", "controller_device_index")
    device_id = initialize.get_device_id('controller', controller_device_index)
    if device_id is None:
        zi_logger.print_error("Failed to get device ID, skipping the test.")
    else:
        zi_logger.print_success(f"Device ID: {device_id}")

def test_onboarding_protocol_de(initialize):
    """
    Test case for onboarding protocol data element.
    """
    zi_logger.print_step("\n Test case for onboarding protocol data element.")
    onboarding_protocol = initialize.get_onboarding_protocol('controller', "controller_device_index")
    if onboarding_protocol is None:
        zi_logger.print_error("Failed to get onboarding protocol, skipping the test.")
    else:
        zi_logger.print_success(f"Onboarding Protocol: {onboarding_protocol}")

def test_last_contact_time_de(initialize):
    """
    Test case for last contact time data element.
    """
    zi_logger.print_step("\n Test case for last contact time data element.")
    last_contact_time = initialize.get_last_contact_time('controller', "controller_device_index")
    if last_contact_time is None:
        zi_logger.print_error("Failed to get last contact time, skipping the test.")
    else:
        zi_logger.print_success(f"Last Contact Time: {last_contact_time}")

def test_easymesh_operation_mode_de(initialize):
    """
    Test case for EasyMesh operation mode data element.
    """
    zi_logger.print_step("\n Test case for EasyMesh operation mode data element.")
    operation_mode = initialize.get_easymesh_operation_mode('controller', "controller_device_index")
    if operation_mode is None:
        zi_logger.print_error("Failed to get EasyMesh operation mode, skipping the test.")
    else:
        zi_logger.print_success(f"EasyMesh Operation Mode: {operation_mode}")

def test_ssid(initialize):
    """
    Test case for SSID data element.
    """
    zi_logger.print_step("Test case for SSID data element.")
    ssid = initialize.get_ssid('controller', "controller_device_index",'de')
    if ssid is None:
        zi_logger.print_error("Failed to get SSID, skipping the test.")
    else:
        zi_logger.print_success(f"SSID: {ssid}")


# ---------------------------------------------------------------------------
# 2.Backhaul Data Elements (24)
# ---------------------------------------------------------------------------


def test_backhaul_linktype_de(initialize):
    """
    Test case for backhaul link type data element.
    """
    zi_logger.print_step("Test case for backhaul link type data element.")
    linktype = initialize.get_backhaul_linktype("controller","controller_device_index")
    if linktype is None:
        zi_logger.print_error("Backhaul link type data element not found.")
    else:
        zi_logger.print_success(f"Backhaul link type data element found: {linktype}")

def test_backhaul_macaddress_de(initialize):
    """
    Test case for backhaul MAC address data element.
    """
    zi_logger.print_step("\nTest case for backhaul MAC address data element.")
    macaddress = initialize.get_backhaul_MACaddress("controller","controller_device_index")
    if macaddress is None:
        zi_logger.print_error("Backhaul MAC address data element not found.")
    else:
        zi_logger.print_success(f"Backhaul MAC address data element found: {macaddress}")

def test_backhaul_backhaul_macaddress_de(initialize):
    """
    Test case for backhaul backhaul MAC address data element.
    """
    zi_logger.print_step("\n Test case for backhaul backhaul MAC address data element.")
    backhaul_macaddress = initialize.get_backhaul_backhaulMACAddress("controller","controller_device_index")
    if backhaul_macaddress is None:
        zi_logger.print_error("Backhaul backhaul MAC address data element not found.")
    else:
        zi_logger.print_success(f"Backhaul backhaul MAC address data element found: {backhaul_macaddress}")

def test_backhaul_backhauluse_de(initialize):
    """
    Test case for backhaul use data element.
    """
    zi_logger.print_step("\nTest case for backhaul use data element.")
    use = initialize.get_backhaul_backhauluse("controller","controller_device_index","2g_radio_index","2g_radio_bss_index")
    if use is None:
        zi_logger.print_error("Backhaul use data element not found.")
    else:
        zi_logger.print_success(f"Backhaul use data element found: {use}")

def test_backhaulsta_MACaddress_de(initialize):
    """
    Test case for backhaul STA MAC address data element.
    """
    zi_logger.print_step("\nTest case for backhaul STA MAC address data element.")
    sta_macaddress = initialize.get_backhaulsta_MACaddress("controller","controller_device_index","2g_radio_index")
    if sta_macaddress is None:
        zi_logger.print_error("Backhaul STA MAC address data element not found.")
    else:
        zi_logger.print_success(f"Backhaul STA MAC address data element found: {sta_macaddress}")

def test_backhaul_stats_signalstrength_de(initialize):
    """
    Test case for backhaul stats signal strength data element.
    """
    zi_logger.print_step("\nTest case for backhaul stats signal strength data element.")
    signalstrength = initialize.get_backhaul_stats_signalstrength("controller","controller_device_index")
    if signalstrength is None:
        zi_logger.print_error("Backhaul stats signal strength data element not found.")
    else:
        zi_logger.print_success(f"Backhaul stats signal strength data element found: {signalstrength}")

def test_controller_id_de(initialize):
    """
    Test case for controller ID data element.
    """
    zi_logger.print_step("\nTest case for controller ID data element.")
    controller_id = initialize.get_controller_id("controller")
    if controller_id is None:
        zi_logger.print_error("Controller ID data element not found.")
    else:
        zi_logger.print_success(f"Controller ID data element found: {controller_id}")

def test_backhaul_stats_bytesent_de(initialize):
    """
    Test case for backhaul stats bytes sent data element.
    """
    zi_logger.print_step("\nTest case for backhaul stats bytes sent data element.")
    bytesent = initialize.get_backhaul_stats_bytessent("controller","controller_device_index")
    if bytesent is None:
        zi_logger.print_error("Backhaul stats bytes sent data element not found.")
    else:
        zi_logger.print_success(f"Backhaul stats bytes sent data element found: {bytesent}")

def test_backhaul_stats_bytesreceived_de(initialize):
    """
    Test case for backhaul stats bytes received data element.
    """
    zi_logger.print_step("\nTest case for backhaul stats bytes received data element.")
    bytesreceived = initialize.get_backhaul_stats_bytesreceived("controller","controller_device_index")
    if bytesreceived is None:
        zi_logger.print_error("Backhaul stats bytes received data element not found.")
    else:
        zi_logger.print_success(f"Backhaul stats bytes received data element found: {bytesreceived}")

def test_backhaul_stats_linkutilization_de(initialize):
    """
    Test case for backhaul stats link utilization data element.
    """
    zi_logger.print_step("\nTest case for backhaul stats link utilization data element.")
    linkutilization = initialize.get_backhaul_stats_linkutilization("controller","controller_device_index")
    if linkutilization is None:
        zi_logger.print_error("Backhaul stats link utilization data element not found.")
    else:
        zi_logger.print_success(f"Backhaul stats link utilization data element found: {linkutilization}")

def test_backhaul_stats_linkdatadownlinkrate_de(initialize):
    """
    Test case for backhaul stats link data downlink rate data element.
    """
    zi_logger.print_step("\nTest case for backhaul stats link data downlink rate data element.")
    downlinkrate = initialize.get_backhaul_stats_lastdatadownlinkrate("controller","controller_device_index")
    if downlinkrate is None:
        zi_logger.print_error("Backhaul stats link data downlink rate data element not found.")
    else:
        zi_logger.print_success(f"Backhaul stats link data downlink rate data element found: {downlinkrate}")

def test_backhaul_stats_linkdatauplinkrate_de(initialize):
    """
    Test case for backhaul stats link data uplink rate data element.
    """
    zi_logger.print_step("\nTest case for backhaul stats link data uplink rate data element.")
    uplinkrate = initialize.get_backhaul_stats_lastdatauplinkrate("controller","controller_device_index")
    if uplinkrate is None:
        zi_logger.print_error("Backhaul stats link data uplink rate data element not found.")
    else:
        zi_logger.print_success(f"Backhaul stats link data uplink rate data element found: {uplinkrate}")

def test_backhaul_status_de(initialize):
    """
    Test case for backhaul status data element.
    """
    zi_logger.print_step("\nTest case for backhaul status data element.")
    status = initialize.get_backhaul_status("controller","controller_device_index")
    if status is None:
        zi_logger.print_error("Backhaul status data element not found.")
    else:
        zi_logger.print_success(f"Backhaul status data element found: {status}")

def test_backhaul_numberofentries_de(initialize):
    """
    Test case for backhaul number of entries data element.
    """
    zi_logger.print_step("\nTest case for backhaul number of entries data element.")
    numberofentries = initialize.get_backhaul_numberofentries("controller")
    if numberofentries is None:
        zi_logger.print_error("Backhaul number of entries data element not found.")
    else:
        zi_logger.print_success(f"Backhaul number of entries data element found: {numberofentries}")

def test_preferred_backhauls_MACaddress_de(initialize):
    """
    Test case for preferred backhauls MAC address data element.
    """
    zi_logger.print_step("\nTest case for preferred backhauls MAC address data element.")
    preferred_macaddress = initialize.get_preferredbackhauls_MACaddress("controller","controller_device_index")
    if preferred_macaddress is None:
        zi_logger.print_error("Preferred backhauls MAC address data element not found.")
    else:
        zi_logger.print_success(f"Preferred backhauls MAC address data element found: {preferred_macaddress}")

def test_preferredbackhauls_bstaMACaddress_de(initialize):
    """
    Test case for preferred backhauls BSTA MAC address data element.
    """
    zi_logger.print_step("\nTest case for preferred backhauls BSTA MAC address data element.")
    preferred_bsta_macaddress = initialize.get_preferredbackhauls_bstaMACaddress("controller","controller_device_index")
    if preferred_bsta_macaddress is None:
        zi_logger.print_error("Preferred backhauls BSTA MAC address data element not found.")
    else:
        zi_logger.print_success(f"Preferred backhauls BSTA MAC address data element found: {preferred_bsta_macaddress}")

def test_backhaul_downMACaddress_de(initialize):
    """
    Test case for backhaul down MAC address data element.
    """
    zi_logger.print_step("\nTest case for backhaul down MAC address data element.")
    down_macaddress = initialize.get_backhaul_downMACaddress("controller","controller_device_index")
    if down_macaddress is None:
        zi_logger.print_error("Backhaul down MAC address data element not found.")
    else:
        zi_logger.print_success(f"Backhaul down MAC address data element found: {down_macaddress}")

def test_backhaulalid_de(initialize):
    """
    Test case for backhaul ALID data element.
    """
    zi_logger.print_step("\nTest case for backhaul ALID data element.")
    backhaul_alid = initialize.get_backhaul_alid("controller","controller_device_index")
    if backhaul_alid is None:
        zi_logger.print_error("Backhaul ALID data element not found.")
    else:
        zi_logger.print_success(f"Backhaul ALID data element found: {backhaul_alid}")

def test_backhaulmediatype_de(initialize):
    """
    Test case for backhaul media type data element.
    """
    zi_logger.print_step("\nTest case for backhaul media type data element.")
    backhaul_mediatype = initialize.get_backhaul_mediatype("controller","controller_device_index")
    if backhaul_mediatype is None:
        zi_logger.print_error("Backhaul media type data element not found.")
    else:
        zi_logger.print_success(f"Backhaul media type data element found: {backhaul_mediatype}")

def test_backhaul_akmsallowed_de(initialize):
    """
    Test case for backhaul AKMS allowed data element.
    """
    zi_logger.print_step("\nTest case for backhaul AKMS allowed data element.")
    backhaul_akmsallowed = initialize.get_backhaul_akmsallowed("controller","controller_device_index","2g_radio_index","2g_radio_bss_index")
    if backhaul_akmsallowed is None:
        zi_logger.print_error("Backhaul AKMS allowed data element not found.")
    else:
        zi_logger.print_success(f"Backhaul AKMS allowed data element found: {backhaul_akmsallowed}")

def test_backhaul_backhaulmediatype_de(initialize):
    """
    Test case for backhaul backhaul media type data element.
    """
    zi_logger.print_step("\nTest case for backhaul backhaul media type data element.")
    backhaul_backhaulmediatype = initialize.get_backhaul_backhaulmediatype("controller","controller_device_index")
    if backhaul_backhaulmediatype is None:
        zi_logger.print_error("Backhaul backhaul media type data element not found.")
    else:
        zi_logger.print_success(f"Backhaul backhaul media type data element found: {backhaul_backhaulmediatype}")

def test_backhaul_backhaulphyrate_de(initialize):
    """
    Test case for backhaul backhaul PHY rate data element.
    """
    zi_logger.print_step("\nTest case for backhaul backhaul PHY rate data element.")
    backhaul_phy_rate = initialize.get_backhaul_backhaulphyrate("controller","controller_device_index")
    if backhaul_phy_rate is None:
        zi_logger.print_error("Backhaul backhaul PHY rate data element not found.")
    else:
        zi_logger.print_success(f"Backhaul backhaul PHY rate data element found: {backhaul_phy_rate}")

def test_backhaul_backhauldeviceid_de(initialize):
    """
    Test case for backhaul backhaul device ID data element.
    """
    zi_logger.print_step("\nTest case for backhaul backhaul device ID data element.")
    backhaul_device_id = initialize.get_backhaul_backhauldeviceid("controller","controller_device_index")
    if backhaul_device_id is None:
        zi_logger.print_error("Backhaul backhaul device ID data element not found.")
    else:
        zi_logger.print_success(f"Backhaul backhaul device ID data element found: {backhaul_device_id}")

def test_backhaul_backhaulalid_de(initialize):
    """
    Test case for backhaul backhaul ALID data element.
    """
    zi_logger.print_step("\nTest case for backhaul backhaul ALID data element.")
    backhaul_backhaul_alid = initialize.get_backhaul_backhaulALID("controller","controller_device_index")
    if backhaul_backhaul_alid is None:
        zi_logger.print_error("Backhaul backhaul ALID data element not found.")
    else:
        zi_logger.print_success(f"Backhaul backhaul ALID data element found: {backhaul_backhaul_alid}")

# ---------------------------------------------------------------------------
# 3. Radio Data Elements (8)
# ---------------------------------------------------------------------------

def test_radio_status_de(initialize):
    """
    Test case for radio status data element.
    """
    zi_logger.print_step("\nTest case for radio status data element.")
    radio_status = initialize.get_radio_status("controller","controller_device_index","2g_radio_index")
    if radio_status is None:
        zi_logger.print_error("Radio status data element not found.")
    else:
        zi_logger.print_success(f"Radio status data element found: {radio_status}")

def test_radio_enabled_de(initialize):
    """
    Test case for radio enabled data element.
    """
    zi_logger.print_step("\nTest case for radio enabled data element.")
    radio_enabled = initialize.get_radio_enabled("controller","controller_device_index","2g_radio_index")
    if radio_enabled is None:
        zi_logger.print_error("Radio enabled data element not found.")
    else:
        zi_logger.print_success(f"Radio enabled data element found: {radio_enabled}")

def test_radio_numberofentries_de(initialize):
    """
    Test case for radio number of entries data element.
    """
    zi_logger.print_step("\nTest case for radio number of entries data element.")
    radio_numberofentries = initialize.get_radioNumberofentries("controller","controller_device_index")
    if radio_numberofentries is None:
        zi_logger.print_error("Radio number of entries data element not found.")
    else:
        zi_logger.print_success(f"Radio number of entries data element found: {radio_numberofentries}")

def test_radio_bss_ssid_de(initialize):
    """
    Test case for radio BSS SSID data element.
    """
    zi_logger.print_step("\nTest case for radio BSS SSID data element.")
    bss_ssid = initialize.get_radio_bss_ssid("controller","controller_device_index","2g_radio_index","2g_radio_bss_index")
    if bss_ssid is None:
        zi_logger.print_error("Radio BSS SSID data element not found.")
    else:
        zi_logger.print_success(f"Radio BSS SSID data element found: {bss_ssid}")

def test_currentoperatingprofile_opclass_de(initialize):
    """
    Test case for current operating profile opclass data element.
    """
    zi_logger.print_step("\nTest case for current operating profile opclass data element.")
    opclass = initialize.get_currentoperatingprofile_opclass("controller","controller_device_index","2g_radio_index","profile_index")
    if opclass is None:
        zi_logger.print_error("Current operating profile opclass data element not found.")
    else:
        zi_logger.print_success(f"Current operating profile opclass data element found: {opclass}")

def test_currentoperatingprofile_channel_de(initialize):
    """
    Test case for current operating profile channel data element.
    """
    zi_logger.print_step("\nTest case for current operating profile channel data element.")
    channel = initialize.get_currentoperatingprofile_channel("controller","controller_device_index","2g_radio_index","profile_index")
    if channel is None:
        zi_logger.print_error("Current operating profile channel data element not found.")
    else:
        zi_logger.print_success(f"Current operating profile channel data element found: {channel}")

def test_radio_bss_STANumberofentries_de(initialize):
    """
    Test case for radio BSS STA number of entries data element.
    """
    zi_logger.print_step("\nTest case for radio BSS STA number of entries data element.")
    bss_sta_numberofentries = initialize.get_radio_bss_STANumberOFEntries("controller","controller_device_index","2g_radio_index","2g_radio_bss_index")
    if bss_sta_numberofentries is None:
        zi_logger.print_error("Radio BSS STA number of entries data element not found.")
    else:
        zi_logger.print_success(f"Radio BSS STA number of entries data element found: {bss_sta_numberofentries}")  

def test_radio_bss_STA_MACaddress_de(initialize):
    """
    Test case for radio BSS STA MAC address data element.
    """
    zi_logger.print_step("\nTest case for radio BSS STA MAC address data element.")
    bss_sta_macaddress = initialize.get_radio_bss_STA_MACAddress("controller","controller_device_index","2g_radio_index","2g_radio_bss_index","sta_index")
    if bss_sta_macaddress is None:
        zi_logger.print_error("Radio BSS STA MAC address data element not found.")
    else:
        zi_logger.print_success(f"Radio BSS STA MAC address data element found: {bss_sta_macaddress}")

# ---------------------------------------------------------------------------
# 4. Client Association Data Elements (13)
# ---------------------------------------------------------------------------

def test_ssid_AKMAllowed_de(initialize):
    """
    Test case for SSID AKM Allowed data element.
    """
    zi_logger.print_step("Test case for SSID AKM Allowed data element.")
    akm_allowed = initialize.get_ssid_AKMAllowed('controller', "controller_device_index")
    if akm_allowed is None:
        zi_logger.print_error("Failed to get SSID AKM Allowed, skipping the test.")
    else:
        zi_logger.print_success(f"SSID AKM Allowed: {akm_allowed}")

def test_ssid_MFPConfig_de(initialize):
    """
    Test case for SSID MFP Config data element.
    """
    zi_logger.print_step("Test case for SSID MFP Config data element.")
    mfp_config = initialize.get_ssid_MFPConfig('controller', "controller_device_index")
    if mfp_config is None:
        zi_logger.print_error("Failed to get SSID MFP Config, skipping the test.")
    else:
        zi_logger.print_success(f"SSID MFP Config: {mfp_config}")

def test_ssid_keyPassphrase_de(initialize):
    """
    Test case for SSID Key Passphrase data element.
    """
    zi_logger.print_step("Test case for SSID Key Passphrase data element.")
    key_passphrase = initialize.get_ssid_KeyPassphrase('controller', "controller_device_index")
    if key_passphrase is None:
        zi_logger.print_error("Failed to get SSID Key Passphrase, skipping the test.")
    else:
        zi_logger.print_success(f"SSID Key Passphrase: {key_passphrase}")

def test_dhcpv4_server_enable_de(initialize):
    """
    Test case for DHCPv4 Server Enable data element.
    """
    zi_logger.print_step("Test case for DHCPv4 Server Enable data element.")
    dhcpv4_enable = initialize.get_dhcpv4_server_enable('controller')
    if dhcpv4_enable is None:
        zi_logger.print_error("Failed to get DHCPv4 Server Enable, skipping the test.")
    else:
        zi_logger.print_success(f"DHCPv4 Server Enable: {dhcpv4_enable}")

def test_dhcpv4_server_pool_Maxaddress_de(initialize):
    """
    Test case for DHCPv4 Server Pool Max Address data element.
    """
    zi_logger.print_step("Test case for DHCPv4 Server Pool Max Address data element.")
    max_address = initialize.get_dhcpv4_server_pool_Maxaddress('controller',"controller_device_index")
    if max_address is None:
        zi_logger.print_error("Failed to get DHCPv4 Server Pool Max Address, skipping the test.")
    else:
        zi_logger.print_success(f"DHCPv4 Server Pool Max Address: {max_address}")

def test_dhcpv4_server_pool_client_chaddr_de(initialize):
    """
    Test case for DHCPv4 Server Pool Client CHADDR data element.
    """
    zi_logger.print_step("Test case for DHCPv4 Server Pool Client CHADDR data element.")
    client_chaddr = initialize.get_dhcpv4_server_pool_client_Chaddr('controller',"controller_device_index","sta_index")
    if client_chaddr is None:
        zi_logger.print_error("Failed to get DHCPv4 Server Pool Client CHADDR, skipping the test.")
    else:
        zi_logger.print_success(f"DHCPv4 Server Pool Client CHADDR: {client_chaddr}")

def test_dhcpv4_server_pool_client_number_of_entries_de(initialize):
    """
    Test case for DHCPv4 Server Pool Client Number of Entries data element.
    """
    zi_logger.print_step("Test case for DHCPv4 Server Pool Client Number of Entries data element.")
    num_entries = initialize.get_dhcpv4_server_pool_clientNumberOfEntries('controller', "controller_device_index")
    if num_entries is None:
        zi_logger.print_error("Failed to get DHCPv4 Server Pool Client Number of Entries, skipping the test.")
    else:
        zi_logger.print_success(f"DHCPv4 Server Pool Client Number of Entries: {num_entries}")

def test_IP_Interface_Enable_de(initialize):
    """
    Test case for IP Interface Enable data element.
    """
    zi_logger.print_step("Test case for IP Interface Enable data element.")
    ip_interface_enable = initialize.get_IP_Interface_Enable('controller', "controller_device_index")
    if ip_interface_enable is None:
        zi_logger.print_error("Failed to get IP Interface Enable, skipping the test.")
    else:
        zi_logger.print_success(f"IP Interface Enable: {ip_interface_enable}")

def test_IP_Interface_IPv4Address_IPAddress_de(initialize):
    """
    Test case for IP Interface IPv4 Address data element.
    """
    zi_logger.print_step("Test case for IP Interface IPv4 Address data element.")
    ip_address = initialize.get_IP_Interface_IPv4Address_IPAddress('controller', "controller_device_index","ip_index")
    if ip_address is None:
        zi_logger.print_error("Failed to get IP Interface IPv4 Address, skipping the test.")
    else:
        zi_logger.print_success(f"IP Interface IPv4 Address: {ip_address}")

def test_Router_Enable_de(initialize):
    """
    Test case for Router Enable data element.
    """
    zi_logger.print_step("Test case for Router Enable data element.")
    router_enable = initialize.get_Router_Enable('controller', "controller_device_index")
    if router_enable is None:
        zi_logger.print_error("Failed to get Router Enable, skipping the test.")
    else:
        zi_logger.print_success(f"Router Enable: {router_enable}")

def test_DHCPv4_Server_Pool_Client_IPv4Address_IPAddress_de(initialize):
    """
    Test case for DHCPv4 Server Pool Client IPv4 Address data element.
    """
    zi_logger.print_step("Test case for DHCPv4 Server Pool Client IPv4 Address data element.")
    dhcp_client_ip = initialize.get_DHCPv4_Server_Pool_Client_IPv4Address_IPAddress('controller',"controller_device_index","sta_index","ip_index")
    if dhcp_client_ip is None:
        zi_logger.print_error("Failed to get DHCPv4 Server Pool Client IPv4 Address, skipping the test.")
    else:
        zi_logger.print_success(f"DHCPv4 Server Pool Client IPv4 Address: {dhcp_client_ip}")

def test_sta_BytesSent_de(initialize):
    """
    Test case for STA Bytes Sent data element.
    """
    zi_logger.print_step("Test case for STA Bytes Sent data element.")
    bytes_sent = initialize.get_sta_BytesSent('controller', "controller_device_index","2g_radio_index","2g_radio_bss_index","sta_index")
    if bytes_sent is None:
        zi_logger.print_error("Failed to get STA Bytes Sent, skipping the test.")
    else:
        zi_logger.print_success(f"STA Bytes Sent: {bytes_sent}")

def test_sta_BytesReceived_de(initialize):
    """
    Test case for STA Bytes Received data element.
    """
    zi_logger.print_step("Test case for STA Bytes Received data element.")
    bytes_received = initialize.get_sta_BytesReceived('controller', "controller_device_index","2g_radio_index","2g_radio_bss_index","sta_index")
    if bytes_received is None:
        zi_logger.print_error("Failed to get STA Bytes Received, skipping the test.")
    else:
        zi_logger.print_success(f"STA Bytes Received: {bytes_received}")



