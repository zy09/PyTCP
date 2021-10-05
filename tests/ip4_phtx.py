#!/usr/bin/env python3


############################################################################
#                                                                          #
#  PyTCP - Python TCP/IP stack                                             #
#  Copyright (C) 2020-2021  Sebastian Majewski                             #
#                                                                          #
#  This program is free software: you can redistribute it and/or modify    #
#  it under the terms of the GNU General Public License as published by    #
#  the Free Software Foundation, either version 3 of the License, or       #
#  (at your option) any later version.                                     #
#                                                                          #
#  This program is distributed in the hope that it will be useful,         #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#  GNU General Public License for more details.                            #
#                                                                          #
#  You should have received a copy of the GNU General Public License       #
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.  #
#                                                                          #
#  Author's email: ccie18643@gmail.com                                     #
#  Github repository: https://github.com/ccie18643/PyTCP                   #
#                                                                          #
############################################################################


#
# tests/ip4_phtx.py -  tests specific for IPv4 phtx module
#

from __future__ import annotations  # Required by Python ver < 3.10

from testslide import TestCase

from pytcp.misc.packet_stats import PacketStatsTx
from tests.mock_network import (
    MockNetworkSettings,
    patch_config,
    setup_mock_packet_handler,
)

TEST_FRAME_DIR = "tests/test_frames/ip4_phtx/"


class TestIp4Phtx(TestCase):
    def setUp(self):
        super().setUp()

        self.mns = MockNetworkSettings()
        patch_config(self)
        setup_mock_packet_handler(self)

    # Test name format: 'test_name__test_description__optional_condition'
    
    def test_ip4_phtx__ip4_to_unicast_address_on_local_network__src_valid(self):
        """Test sending IPv4 packet to unicast address on local network / valid source"""

        tx_status = self.packet_handler._phtx_ip4(
            ip4_src=self.mns.stack_ip4_host.address,
            ip4_dst=self.mns.host_a_ip4_address,
        )
        self.assertEqual(str(tx_status), "PASSED_TO_TX_RING")
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip4__pre_assemble=1,
                ip4__mtu_ok__send=1,
                ether__pre_assemble=1,
                ether__src_unspec__fill=1,
                ether__dst_unspec__ip4_lookup=1,
                ether__dst_unspec__ip4_lookup__locnet__arp_cache_hit__send=1,
            ),
        )
        with open(TEST_FRAME_DIR + "ip4_to_unicast_address_on_local_network__src_valid.tx", "rb") as _:
            frame_tx = _.read()
        self.assertEqual(self.frame_tx[: len(frame_tx)], frame_tx)

    def test_ip4_phtx__ip4_to_unicast_address_on_local_network__src_not_owned_drop(self):
        """Test sending IPv4 packet to unicast address on local network / src not owned"""

        tx_status = self.packet_handler._phtx_ip4(
            ip4_src=self.mns.host_b_ip4_address,
            ip4_dst=self.mns.host_a_ip4_address,
        )
        self.assertEqual(str(tx_status), "DROPED_IP4_INVALID_SOURCE")
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip4__pre_assemble=1,
                ip4__src_not_owned__drop=1,
            ),
        )

    def test_ip4_phtx__ip4_to_unicast_address_on_local_network__src_multicast_replace(self):
        """Test sending IPv4 packet to unicast address on local network / multicast source, able to replace"""

        tx_status = self.packet_handler._phtx_ip4(
            ip4_src=self.mns.ip4_multicast_all_nodes,
            ip4_dst=self.mns.host_a_ip4_address,
        )
        self.assertEqual(str(tx_status), "PASSED_TO_TX_RING")
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip4__pre_assemble=1,
                ip4__src_multicast__replace=1,
                ip4__mtu_ok__send=1,
                ether__pre_assemble=1,
                ether__src_unspec__fill=1,
                ether__dst_unspec__ip4_lookup=1,
                ether__dst_unspec__ip4_lookup__locnet__arp_cache_hit__send=1,
            ),
        )
        with open(TEST_FRAME_DIR + "ip4_to_unicast_address_on_local_network__src_multicast_replace.tx", "rb") as _:
            frame_tx = _.read()
        self.assertEqual(self.frame_tx[: len(frame_tx)], frame_tx)

    def test_ip4_phtx__ip4_to_unicast_address_on_local_network__src_multicast_drop(self):
        """Test sending IPv4 packet to unicast address on local network / multicast source, not able to replace"""

        self.packet_handler.ip4_host = []

        tx_status = self.packet_handler._phtx_ip4(
            ip4_src=self.mns.ip4_multicast_all_nodes,
            ip4_dst=self.mns.host_a_ip4_address,
        )
        self.assertEqual(str(tx_status), "DROPED_IP4_INVALID_SOURCE")
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip4__pre_assemble=1,
                ip4__src_multicast__drop=1,
            ),
        )

    def test_ip4_phtx__ip4_to_unicast_address_on_local_network__src_limited_broadcast_replace(self):
        """Test sending IPv4 packet to unicast address on local network / limited broadcst source, able to replace"""

        tx_status = self.packet_handler._phtx_ip4(
            ip4_src=self.mns.ip4_limited_broadcast,
            ip4_dst=self.mns.host_a_ip4_address,
        )
        self.assertEqual(str(tx_status), "PASSED_TO_TX_RING")
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip4__pre_assemble=1,
                ip4__src_limited_broadcast__replace=1,
                ip4__mtu_ok__send=1,
                ether__pre_assemble=1,
                ether__src_unspec__fill=1,
                ether__dst_unspec__ip4_lookup=1,
                ether__dst_unspec__ip4_lookup__locnet__arp_cache_hit__send=1,
            ),
        )
        with open(TEST_FRAME_DIR + "ip4_to_unicast_address_on_local_network__src_limited_broadcast_replace.tx", "rb") as _:
            frame_tx = _.read()
        self.assertEqual(self.frame_tx[: len(frame_tx)], frame_tx)

    def test_ip4_phtx__ip4_to_unicast_address_on_local_network__src_limited_broadcast_drop(self):
        """Test sending IPv4 packet to unicast address on local network / limited broadcast source, not able to replace"""

        self.packet_handler.ip4_host = []

        tx_status = self.packet_handler._phtx_ip4(
            ip4_src=self.mns.ip4_limited_broadcast,
            ip4_dst=self.mns.host_a_ip4_address,
        )
        self.assertEqual(str(tx_status), "DROPED_IP4_INVALID_SOURCE")
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip4__pre_assemble=1,
                ip4__src_limited_broadcast__drop=1,
            ),
        )

    def test_ip4_phtx__ip4_to_unicast_address_on_local_network__src_network_broadcast_replace(self):
        """Test sending IPv4 packet to unicast address on local network / network broadcst source, able to replace"""

        tx_status = self.packet_handler._phtx_ip4(
            ip4_src=self.mns.stack_ip4_host.network.broadcast,
            ip4_dst=self.mns.host_a_ip4_address,
        )
        self.assertEqual(str(tx_status), "PASSED_TO_TX_RING")
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip4__pre_assemble=1,
                ip4__src_network_broadcast__replace=1,
                ip4__mtu_ok__send=1,
                ether__pre_assemble=1,
                ether__src_unspec__fill=1,
                ether__dst_unspec__ip4_lookup=1,
                ether__dst_unspec__ip4_lookup__locnet__arp_cache_hit__send=1,
            ),
        )
        with open(TEST_FRAME_DIR + "ip4_to_unicast_address_on_local_network__src_multicast_replace.tx", "rb") as _:
            frame_tx = _.read()
        self.assertEqual(self.frame_tx[: len(frame_tx)], frame_tx)

    def test_ip4_phtx__ip4_to_unicast_address_on_local_network__src_unspecified_replace(self):
        """Test sending IPv4 packet to unicast address on local network / uspecified source, able to replace"""

        tx_status = self.packet_handler._phtx_ip4(
            ip4_src=self.mns.ip4_unspecified,
            ip4_dst=self.mns.host_a_ip4_address,
        )
        self.assertEqual(str(tx_status), "PASSED_TO_TX_RING")
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip4__pre_assemble=1,
                ip4__src_unspecified__replace=1,
                ip4__mtu_ok__send=1,
                ether__pre_assemble=1,
                ether__src_unspec__fill=1,
                ether__dst_unspec__ip4_lookup=1,
                ether__dst_unspec__ip4_lookup__locnet__arp_cache_hit__send=1,
            ),
        )
        with open(TEST_FRAME_DIR + "ip4_to_unicast_address_on_local_network__src_unspecified_replace.tx", "rb") as _:
            frame_tx = _.read()
        self.assertEqual(self.frame_tx[: len(frame_tx)], frame_tx)

    def test_ip4_phtx__ip4_to_unicast_address_on_local_network__src_unspecified_replace_by_stack_address_with_gateway(self):
        """Test sending IPv4 packet to unicast address on local network / uspecified source, able to replace with ip from subnet with gateway"""

        tx_status = self.packet_handler._phtx_ip4(
            ip4_src=self.mns.ip4_unspecified,
            ip4_dst=self.mns.host_a_ip4_address,
        )
        self.assertEqual(str(tx_status), "PASSED_TO_TX_RING")
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip4__pre_assemble=1,
                ip4__src_unspecified__replace=1,
                ip4__mtu_ok__send=1,
                ether__pre_assemble=1,
                ether__src_unspec__fill=1,
                ether__dst_unspec__ip4_lookup=1,
                ether__dst_unspec__ip4_lookup__locnet__arp_cache_hit__send=1,
            ),
        )
        with open(TEST_FRAME_DIR + "ip4_to_unicast_address_on_local_network__src_unspecified_replace_by_stack_address_with_gateway.tx", "rb") as _:
            frame_tx = _.read()
        self.assertEqual(self.frame_tx[: len(frame_tx)], frame_tx)

    def test_ip4_phtx__ip4_to_unicast_address_on_local_network__src_unspecified_drop(self):
        """Test sending IPv4 packet to unicast address on local network / uspecified source, not able to replace"""

        self.mns.stack_ip4_host.gateway = None

        tx_status = self.packet_handler._phtx_ip4(
            ip4_src=self.mns.ip4_unspecified,
            ip4_dst=self.mns.host_c_ip4_address,
        )
        self.assertEqual(str(tx_status), "DROPED_IP4_INVALID_SOURCE")
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip4__pre_assemble=1,
                ip4__src_unspecified__drop=1,
            ),
        )