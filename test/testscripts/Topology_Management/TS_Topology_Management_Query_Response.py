# If not stated otherwise in this file or this component LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2026 RDK Management
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

import os
import time
from packet_analyzer.packet_dissector import *
from rdkbmeshzap.common_utils import device_utils, report_logger

def test_topology_management_query_response_capture(initialize):
    """
    Restart each enabled Extender's em_agent and validate the captured
    Topology Query/Response traffic and newly generated core dumps.
    """
    report_logger.print_test("Entering test_topology_management_query_response_capture")
    pcap_filename = None
    capture_started = False
    
    try:
        # Identify the enabled Extenders included in this validation.
        report_logger.print_step("STEP 1: Discover enabled Extenders")
        extenders = device_utils.get_enabled_extenders(initialize)
        if not extenders:
            report_logger.print_error("FAIL: No enabled Extenders found in the testbed")
            return
        report_logger.print_info(f"INFO: Found {len(extenders)} enabled Extenders")

        # Save device identities and timestamps before restarting services.
        report_logger.print_step("STEP 2: Record Extender AL MAC addresses and timestamps for validation")
        extender_al_macs = {}
        restart_timestamps = {}
        controller_al_mac = initialize.get_al_mac_address("controller", "cli").lower()
        for extender in extenders:
            extender_al_macs[extender] = initialize.get_al_mac_address(extender, "cli").lower()
            restart_timestamps[extender] = initialize.get_time_stamp(extender)
        report_logger.print_info("INFO: Recorded Controller and Extender AL MAC addresses and pre-restart timestamps")

        # Capture on the Controller before restarting agents.
        pcap_filename = device_utils.start_capture(initialize, "controller", "topology_management_query_response", step=3)
        capture_started = True
        
        # Restart em_agent on every enabled Extender.
        report_logger.print_step("STEP 4: Restart em_agent on each enabled Extender")
        for extender in extenders:
            try:
                report_logger.print_info(f"INFO: Restarting em_agent on {extender}")
                initialize.restart_service(extender, "em_agent")
            except Exception as error:
                report_logger.print_error(f"FAIL: Could not restart em_agent on {extender}: {error}")
                return

        # Confirm each restarted service is active before checking packets.
        report_logger.print_step("STEP 5: Verify em_agent is active on each enabled Extender")
        service_status_failed = False
        for extender in extenders:
            if not device_utils.verify_services(
                initialize,
                extender,
                ("em_agent",),
                deadline=time.monotonic() + 60,
            ):
                service_status_failed = True
                continue
            report_logger.print_success(f"PASS: em_agent is active on {extender} after restart")
        if service_status_failed:
            return

        # Leave time for topology packets to appear in the capture.
        report_logger.print_step("STEP 6: Wait 30 seconds for topology packets to propagate")
        time.sleep(30)
        report_logger.print_info("INFO: Topology packet propagation period complete")

        # Stop the capture and retrieve the PCAP for analysis.
        report_logger.print_step("STEP 7: Stop and collect the Controller packet capture")
        pcap_file = device_utils.stop_and_collect_capture(initialize, "controller", pcap_filename)
        capture_started = False
        if not pcap_file or not os.path.isfile(pcap_file):
            report_logger.print_error(f"FAIL: Captured PCAP was not downloaded: {pcap_file!r}")
            return

        # Check that the service restart did not produce new core dumps.
        report_logger.print_step("STEP 8: Verify each Extender has no new core dumps after restart")
        for extender in extenders:
            try:
                new_core_dumps = initialize.get_core_dump_status(extender, restart_timestamps[extender])
            except Exception as error:
                report_logger.print_error(f"FAIL: Could not check for new core dumps on {extender}: {error}")
                continue
            if new_core_dumps:
                report_logger.print_error(f"FAIL: New core dump(s) found on {extender}: {sorted(new_core_dumps)}")
            else:
                report_logger.print_success(f"PASS: No new core dumps found on {extender}")
        
        # Reassemble fragmented IEEE 1905 messages from the capture.
        report_logger.print_step("STEP 9: Reassemble and analyze captured IEEE 1905 packets")
        reassembled_packets = reassemble_packets(pcap_file)
        if not reassembled_packets:
            report_logger.print_error("FAIL: No IEEE 1905 packets were found in the controller capture")
            return
        report_logger.print_info(f"INFO: Reassembled {len(reassembled_packets)} IEEE 1905 packets from the controller capture")
        
        # Find queries and responses exchanged between the Controller and each Extender.
        report_logger.print_step("STEP 10: Find Topology Queries and Responses for each Extender")
        query_payloads_by_extender = {}
        response_payloads_by_extender = {}
        for extender, al_mac in extender_al_macs.items():
            query_payloads = check_message_presence(
                reassembled_packets, 0x0002, src_mac=controller_al_mac, dst_mac=al_mac
            ) or []
            response_payloads = check_message_presence(
                reassembled_packets, 0x0003, src_mac=al_mac, dst_mac=controller_al_mac
            ) or []
            query_payloads_by_extender[extender] = query_payloads
            response_payloads_by_extender[extender] = response_payloads
            if not query_payloads:
                report_logger.print_error(f"FAIL: No Topology Query message was captured for {extender}; captured {len(response_payloads)} Topology Response messages")
            if not response_payloads:
                report_logger.print_error(f"FAIL: No Topology Response message was captured for {extender}; captured {len(query_payloads)} Topology Query messages")
            if query_payloads and response_payloads:
                report_logger.print_info(
                    f"INFO: {extender}: captured {len(query_payloads)} Topology Query "
                    f"and {len(response_payloads)} Topology Response messages"
                )
        if not any(
            query_payloads_by_extender[extender]
            and response_payloads_by_extender[extender]
            for extender in extenders
        ):
            return

        # Ensure each Extender's responses reference IDs from its queries.
        report_logger.print_step("STEP 11: Verify each Extender's Topology Responses match its Queries")
        for extender in extenders:
            if not query_payloads_by_extender[extender] or not response_payloads_by_extender[extender]:
                continue
            try:
                query_ids = extract_message_ids_from_payloads(query_payloads_by_extender[extender])
                response_ids = [
                    next(iter(extract_message_ids_from_payloads([payload])))
                    for payload in response_payloads_by_extender[extender]
                ]
            except ValueError as error:
                report_logger.print_error(f"FAIL: Invalid Topology message payload for {extender}: {error}")
                continue
            unmatched_responses = [
                message_id for message_id in response_ids if message_id not in query_ids
            ]
            if unmatched_responses:
                report_logger.print_error(
                    f"FAIL: {extender} has Topology Responses without matching Queries: "
                    + ", ".join(f"0x{mid:04X}" for mid in sorted(set(unmatched_responses)))
                )
            else:
                report_logger.print_success(
                    f"PASS: All {len(response_ids)} Topology Response messages for {extender} "
                    f"have IDs matching its Topology Query IDs ({len(set(response_ids))} unique IDs)"
                )
        
    finally:
        try:
            if capture_started:
                device_utils.stop_and_collect_capture(initialize, "controller", pcap_filename)
        except Exception as cleanup_error:
            report_logger.print_error(f"FAIL: Cleanup failed: {cleanup_error}")        
        report_logger.print_test("Exiting test_topology_management_query_response_capture")
