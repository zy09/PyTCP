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
# tests/ip6_phtx.py -  tests specific for IPv6 phtx module
#


from protocols.raw.fpa import RawAssembler
from testslide import TestCase

from pytcp.misc.packet_stats import PacketStatsTx
from pytcp.misc.tx_status import TxStatus
from tests.mock_network import (
    MockNetworkSettings,
    patch_config,
    setup_mock_packet_handler,
)

TEST_FRAME_DIR = "tests/test_frames/ip6_phtx/"


class TestIp6Phtx(TestCase):
    def setUp(self):
        super().setUp()

        self.mns = MockNetworkSettings()
        patch_config(self)
        setup_mock_packet_handler(self)

    # Test name format: 'test_name__test_description__optional_condition'

    def test_ip6_phtx__ip6_to_unicast_address_on_local_network__src_valid(self):
        """Test sending IPv6 packet to unicast address on local network / valid source"""

        tx_status = self.packet_handler._phtx_ip6(
            ip6_src=self.mns.stack_ip6_host.address,
            ip6_dst=self.mns.host_a_ip6_address,
        )
        self.assertEqual(tx_status, TxStatus.PASSED__ETHER__TO_TX_RING)
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip6__pre_assemble=1,
                ip6__mtu_ok__send=1,
                ether__pre_assemble=1,
                ether__src_unspec__fill=1,
                ether__dst_unspec__ip6_lookup=1,
                ether__dst_unspec__ip6_lookup__locnet__nd_cache_hit__send=1,
            ),
        )
        with open(TEST_FRAME_DIR + "ip6_to_unicast_address_on_local_network__src_valid.tx", "rb") as _:
            frame_tx = _.read()
        self.assertEqual(self.frame_tx[: len(frame_tx)], frame_tx)

    def test_ip6_phtx__ip6_to_unicast_address_on_local_network__src_not_owned_drop(self):
        """Test sending IPv6 packet to unicast address on local network / src not owned"""

        tx_status = self.packet_handler._phtx_ip6(
            ip6_src=self.mns.host_b_ip6_address,
            ip6_dst=self.mns.host_a_ip6_address,
        )
        self.assertEqual(tx_status, TxStatus.DROPED__IP6__SRC_NOT_OWNED)
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip6__pre_assemble=1,
                ip6__src_not_owned__drop=1,
            ),
        )

    def test_ip6_phtx__ip6_to_unicast_address_on_local_network__src_multicast_replace(self):
        """Test sending IPv6 packet to unicast address on local network / multicast source, able to replace"""

        tx_status = self.packet_handler._phtx_ip6(
            ip6_src=self.mns.ip6_multicast_all_nodes,
            ip6_dst=self.mns.host_a_ip6_address,
        )
        self.assertEqual(tx_status, TxStatus.PASSED__ETHER__TO_TX_RING)
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip6__pre_assemble=1,
                ip6__src_multicast__replace=1,
                ip6__mtu_ok__send=1,
                ether__pre_assemble=1,
                ether__src_unspec__fill=1,
                ether__dst_unspec__ip6_lookup=1,
                ether__dst_unspec__ip6_lookup__locnet__nd_cache_hit__send=1,
            ),
        )
        with open(TEST_FRAME_DIR + "ip6_to_unicast_address_on_local_network__src_multicast_replace.tx", "rb") as _:
            frame_tx = _.read()
        self.assertEqual(self.frame_tx[: len(frame_tx)], frame_tx)

    def test_ip6_phtx__ip6_to_unicast_address_on_local_network__src_multicast_drop(self):
        """Test sending IPv6 packet to unicast address on local network / multicast source, not able to replace"""

        self.packet_handler.ip6_host = []

        tx_status = self.packet_handler._phtx_ip6(
            ip6_src=self.mns.ip6_multicast_all_nodes,
            ip6_dst=self.mns.host_a_ip6_address,
        )
        self.assertEqual(tx_status, TxStatus.DROPED__IP6__SRC_MULTICAST)
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip6__pre_assemble=1,
                ip6__src_multicast__drop=1,
            ),
        )

    def test_ip6_phtx__ip6_to_unicast_address_on_local_network__src_unspecified_replace_local(self):
        """Test sending IPv6 packet to unicast address on local network / uspecified source, able to replace"""

        tx_status = self.packet_handler._phtx_ip6(
            ip6_src=self.mns.ip6_unspecified,
            ip6_dst=self.mns.host_a_ip6_address,
        )
        self.assertEqual(tx_status, TxStatus.PASSED__ETHER__TO_TX_RING)
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip6__pre_assemble=1,
                ip6__src_network_unspecified__replace_local=1,
                ip6__mtu_ok__send=1,
                ether__pre_assemble=1,
                ether__src_unspec__fill=1,
                ether__dst_unspec__ip6_lookup=1,
                ether__dst_unspec__ip6_lookup__locnet__nd_cache_hit__send=1,
            ),
        )
        with open(TEST_FRAME_DIR + "ip6_to_unicast_address_on_local_network__src_unspecified_replace_local.tx", "rb") as _:
            frame_tx = _.read()
        self.assertEqual(self.frame_tx[: len(frame_tx)], frame_tx)

    def test_ip6_phtx__ip6_to_unicast_address_on_local_network__src_unspecified_replace_external(self):
        """Test sending IPv6 packet to unicast address on local network / uspecified source, able to replace with ip from subnet with gateway"""

        tx_status = self.packet_handler._phtx_ip6(
            ip6_src=self.mns.ip6_unspecified,
            ip6_dst=self.mns.host_c_ip6_address,
        )
        self.assertEqual(tx_status, TxStatus.PASSED__ETHER__TO_TX_RING)
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip6__pre_assemble=1,
                ip6__src_network_unspecified__replace_external=1,
                ip6__mtu_ok__send=1,
                ether__pre_assemble=1,
                ether__src_unspec__fill=1,
                ether__dst_unspec__ip6_lookup=1,
                ether__dst_unspec__ip6_lookup__extnet__gw_nd_cache_hit__send=1,
            ),
        )
        with open(TEST_FRAME_DIR + "ip6_to_unicast_address_on_local_network__src_unspecified_replace_external.tx", "rb") as _:
            frame_tx = _.read()
        self.assertEqual(self.frame_tx[: len(frame_tx)], frame_tx)

    def test_ip6_phtx__ip6_to_unicast_address_on_local_network__src_unspecified_drop(self):
        """Test sending IPv6 packet to unicast address on local network / uspecified source, not able to replace"""

        self.mns.stack_ip6_host.gateway = None

        tx_status = self.packet_handler._phtx_ip6(
            ip6_src=self.mns.ip6_unspecified,
            ip6_dst=self.mns.host_c_ip6_address,
        )
        self.assertEqual(tx_status, TxStatus.DROPED__IP6__SRC_UNSPECIFIED)
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip6__pre_assemble=1,
                ip6__src_unspecified__drop=1,
            ),
        )

    def test_ip6_phtx__ip6_to_unspecified_address__dst_unspecified_drop(self):
        """Test sending IPv6 packet to unspecified address"""

        self.mns.stack_ip6_host.gateway = None

        tx_status = self.packet_handler._phtx_ip6(
            ip6_src=self.mns.stack_ip6_host.address,
            ip6_dst=self.mns.ip6_unspecified,
        )
        self.assertEqual(tx_status, TxStatus.DROPED__IP6__DST_UNSPECIFIED)
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip6__pre_assemble=1,
                ip6__dst_unspecified__drop=1,
            ),
        )

    def test_ip6_phtx__ip6_fragmentation(self):
        """Test sending IPv6 packet large enough to require fragmentation"""

        self.mns.stack_ip4_host.gateway = None

        tx_status = self.packet_handler._phtx_ip6(
            ip6_src=self.mns.stack_ip6_host.address, ip6_dst=self.mns.host_a_ip6_address, carried_packet=RawAssembler(data=b"01234567890ABCDEF" * 400)
        )
        self.assertEqual(tx_status, TxStatus.PASSED__ETHER__TO_TX_RING)
        self.assertEqual(
            self.packet_handler.packet_stats_tx,
            PacketStatsTx(
                ip6__pre_assemble=6,  # 1 time for initial packet and 5 times for frags
                ip6__mtu_exceed__frag=1,
                ip6__mtu_ok__send=5,
                ip6_ext_frag__pre_assemble=1,
                ip6_ext_frag__send=5,
                ether__pre_assemble=5,
                ether__src_unspec__fill=5,
                ether__dst_unspec__ip6_lookup=5,
                ether__dst_unspec__ip6_lookup__locnet__nd_cache_hit__send=5,
            ),
        )
        for index in range(5):
            with open(f"tests/test_frames/ip6_phtx/ip6_fragmentation__frag_{index}.tx", "rb") as _:
                frame_tx = _.read()
            self.assertEqual(self.frames_tx[index][: len(frame_tx)], frame_tx)
