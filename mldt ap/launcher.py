"""Launcher to run the MLDT apworld client using an ALBW-style interface.

This launcher creates a `CommonContext`-based context, attaches the `N3DSAdapter`
and runs the `MLDTClient.game_watcher` loop so the client can be used with emulators
that expose memory over the same addresses (e.g., Azahar/Citra bridges).
"""

from typing import Optional
import asyncio
import logging
import os
import random
import socket
import struct
import time
import traceback

from CommonClient import ClientCommandProcessor, CommonContext, get_base_parser, server_loop, gui_enabled, logger
from NetUtils import ClientStatus
from Utils import async_start

# DeathLink memory offsets, relative to `self.deathlink_ram_offset` (NOT the
# `azahar_ram_offset`/`self.ram_offset` used for item/shop/block scanning in
# StandaloneMLDTClient.game_watcher the DeathLink struct shifts between NA
# and PAL by a different amount than that one does, so it gets its own base.
#
# Kill method: rather than writing the is-dead flag directly, we force "hero wear"
# onto a bro and push his turn counter to the kill threshold. The game itself then
# applies the kill a pass or two later. Both dead-flag offsets are read-only here.
# Writing the wear+turn values is only ever done right as a battle is entered.
DEATHLINK_DREAM_BATTLE_OFFSET = 0x14173978  # read: region-dependent values -- see DEATHLINK_BATTLE_VALUES (0 = no battle in every region)
DEATHLINK_MARIO_DEAD_OFFSET = 0x1417383C    # read: 0 = dead, 1 = alive
DEATHLINK_LUIGI_DEAD_OFFSET = 0x14174408    # read: 0 = dead, 1 = alive (never touch during a dream battle)
DEATHLINK_MARIO_WEAR_OFFSET = 0x141738B8    # read/write: what Mario is wearing
DEATHLINK_LUIGI_WEAR_OFFSET = 0x14174484    # read/write: what Luigi is wearing (never touch during a dream battle)
DEATHLINK_MARIO_TURN_OFFSET = 0x14173B74    # read/write: Mario's turn count -- reaching the kill threshold while wearing hero wear kills him
DEATHLINK_LUIGI_TURN_OFFSET = 0x14174740    # read/write: Luigi's turn count -- same as above (never touch during a dream battle)
DEATHLINK_MARIO_HP_OFFSET = 0x14173808      # read (2 bytes): used only to confirm a real death, never written
DEATHLINK_LUIGI_HP_OFFSET = 0x141743D4      # read (2 bytes): same, never touch during a dream battle

DEATHLINK_HERO_WEAR_VALUE = 85              # equipment value that arms the turn-count kill
DEATHLINK_KILL_TURN_COUNT = 4               # turn count that triggers the kill once hero wear is equipped
DEATHLINK_ARM_DELAY_SECONDS = 1.5           # wait this long after a battle starts before writing wear/turn

DEATHLINK_MODES = ("gameover", "randombro", "singlebro")

#Used to see if the player is in a menu. Address is the same across regions seemingly.
GAME_STATE_ADDR = 0x857FEE0

triple_addr = ""
is_3ds = False


class ConnectionError(Exception):
    pass


class N3DSAdapter:
    """
    Implements the packet protocol used by Azahar/Citra N3DS memory bridges:
    - UDP port 45987
    - packet header (version, id, type, len)
    - process selection and read/write semantics
    """

    PACKET_VERSION: int = 1
    HEADER_SIZE: int = 0x10
    MAX_PACKET_SIZE: int = 0x410
    TIMEOUT: float = 1.0

    def __init__(self) -> None:
        self.id = 0
        self.max_request_size = 32
        self.sock = None
        self.connected_title_id = None

    def _max_read_size(self) -> int:
        return self.max_request_size

    def _max_write_size(self) -> int:
        return self.max_request_size - 8

    async def _send_packet(self, request_type: int, request_data: bytes, response_size: Optional[int] = None, retry: bool = True) -> bytes:
        loop = asyncio.get_running_loop()
        tries = 4 if retry else 1
        for _ in range(tries):
            try:
                request_id = self.id
                self.id = (self.id + 1) & 0xffffffff
                request = struct.pack("=IIII", self.PACKET_VERSION, request_id, request_type, len(request_data))
                request += request_data
                await asyncio.wait_for(loop.sock_sendall(self.sock, request), self.TIMEOUT)
                for _ in range(16):
                    response = await asyncio.wait_for(loop.sock_recv(self.sock, self.MAX_PACKET_SIZE), self.TIMEOUT)
                    if not response or len(response) < self.HEADER_SIZE:
                        break
                    try:
                        version, id, response_type, size = struct.unpack("=IIII", response[:self.HEADER_SIZE])
                    except Exception as e:
                        logger.debug("_send_packet: bad header unpack: %s", e)
                        continue
                    if version == self.PACKET_VERSION and id == request_id and response_type == request_type:
                        return response[self.HEADER_SIZE:]
            except Exception:
                continue
        raise ConnectionError("Lost connection to game")

    async def _set_process(self, titles) -> bool:
        if isinstance(titles, int):
            titles = {titles}
        else:
            titles = set(titles)
        self.connected_title_id = None
        start_process = 0
        while True:
            request_data = struct.pack("=II", start_process, 0x7fffffff)
            try:
                response = await self._send_packet(3, request_data, retry=False)
                if len(response) < 4:
                    self.max_request_size = 32
                    return False
                count = struct.unpack("=I", response[0:4])[0]
                if count == 0:
                    return False
                start_process += count
                for i in range(count):
                    entry = response[4 + i * 0x14 : 4 + (i + 1) * 0x14]
                    if len(entry) < 0x14:
                        break
                    proc_id, title_id, proc_name = struct.unpack("<IQ8s", entry)
                    proc_name = proc_name.rstrip(b"\x00").decode("ascii", errors="replace")
                    print(f"N3DSAdapter._set_process: candidate proc_id={proc_id} title_id={title_id:#x} process_name={proc_name!r} targets={[f'{t:#x}' for t in titles]}")
                    if title_id in titles:
                        request_data = struct.pack("=II", 1, proc_id)
                        print(f"N3DSAdapter._set_process: selecting proc_id={proc_id} for title {title_id:#x}")
                        await self._send_packet(4, request_data, 0)
                        self.max_request_size = 1024
                        self.connected_title_id = title_id
                        return True
            except ConnectionError:
                print(f"N3DSAdapter._set_process: lost connection while selecting process for titles {[f'{t:#x}' for t in titles]}")
                #logger.warning("N3DSAdapter._set_process: lost connection while selecting process for titles %s", titles)
                self.max_request_size = 32
                return True

    async def connect(self, address: str, title) -> bool:
        try:
            self.disconnect()
        except Exception:
            pass
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Use ALBW default port 45987
        host = address
        port = 45987
        if isinstance(address, str) and ":" in address:
            parts = address.rsplit(":", 1)
            host = parts[0]
            try:
                port = int(parts[1])
            except Exception:
                port = 45987
        self.sock.connect((host, port))
        self.sock.setblocking(False)
        try:
            await self._send_packet(0, b"", 0)
            return await self._set_process(title)
        except ConnectionError:
            return False

    def disconnect(self):
        if hasattr(self, 'sock') and self.sock:
            try:
                self.sock.close()
            except Exception:
                pass

    async def read(self, address: int, size: int) -> bytes:
        mem = b""
        while size > 0:
            request_size = min(size, self._max_read_size())
            request_data = struct.pack("=II", address, request_size)
            mem += await self._send_packet(1, request_data, request_size)
            address += request_size
            size -= request_size
        return mem

    async def write(self, address: int, data: bytes) -> None:
        start = 0
        while start < len(data):
            end = min(start + self._max_write_size(), len(data))
            request_data = struct.pack("=II", address + start, end - start)
            request_data += data[start:end]
            await self._send_packet(2, request_data, 0, retry=False)
            start += self._max_write_size()

    async def read_u32(self, address: int) -> int:
        return int.from_bytes(await self.read(address, 4), "little")

    async def write_u32(self, address: int, value: int) -> None:
        await self.write(address, value.to_bytes(4, "little"))

# How long to wait after a save file is detected as loaded before we start
# trusting game memory / sending items. Gives the game time to finish its
# own loading on 3ds so we don't write items too early.
FILE_LOAD_SETTLE_DELAY = 10


class MLDTCommandProcessor(ClientCommandProcessor):
    def _cmd_3ds(self, address: str):
        """Connect to a real 3DS"""
        global triple_addr
        if triple_addr == "":
            triple_addr = address
            self.output(f"3DS target set to {address}.")
        else:
            self.output(f"Already connected to a 3ds at {triple_addr}.")

    def _cmd_3dsdisconnect(self):
        """Disconnect from the real 3DS target."""
        global triple_addr
        if triple_addr == "":
            self.output("Not currently connected to a 3ds")
        else:
            self.output(f"Disconnected from {triple_addr}.")
            triple_addr = ""

    def _cmd_deathlink(self, mode: str = ""):
        """Configure DeathLink on the fly. Usage: /deathlink [gameover|randombro|singlebro|off]"""
        mode = mode.strip().lower()

        if mode == "":
            self.output("DeathLink commands:")
            self.output("  /deathlink gameover  - send a DeathLink on a game over. "
                        "Receiving a deathlink kills both bros")
            self.output("  /deathlink randombro - send a DeathLink on a game over. Receiving kills a random bro")
                        
            self.output("  /deathlink singlebro - send a DeathLink whenever 1 bro dies. Receiving deathlink kills both")
                        
            self.output("  /deathlink off        - turn DeathLink off.")
            #self.output("  /deathlink debug      - toggle verbose per-pass DeathLink logging.")
            self.output(f"Current mode: {self.ctx.death_link_mode} (debug={self.ctx.death_link_debug}, "
                        f"tags={sorted(self.ctx.tags)}, connected={bool(self.ctx.server)})")
            return True

        if mode == "debug":
            self.ctx.death_link_debug = not self.ctx.death_link_debug
            self.output(f"DeathLink debug logging {'enabled' if self.ctx.death_link_debug else 'disabled'}.")
            return True

        if mode == "off":
            self.ctx.death_link_mode = "off"
            self.ctx.pending_deathlink_kill = False
            async_start(self.ctx.update_death_link(False), name="update_death_link")
            self.output("DeathLink turned off.")
            return True

        if mode not in DEATHLINK_MODES:
            self.output(f"Unknown DeathLink mode '{mode}'. Use /deathlink for the list of commands.")
            return False

        self.ctx.death_link_mode = mode
        async_start(self.ctx.update_death_link(True), name="update_death_link")
        self.output(f"DeathLink mode set to '{mode}'. Tags are now {sorted(self.ctx.tags)}.")
        return True



class StandaloneMLDTClient:
    """Fallback handler that implements the minimal MLDT behaviors needed to
    forward items between the Archipelago server and an N3DS-style emulator
    bridge when the real `mldt` package isn't available.

    It implements ROM validation (reads ROM header to set `ram_offset`) and a
    simplified watcher that mirrors the important parts of the upstream
    `MLDTClient.game_watcher` so items and checks are forwarded.
    """


    ram_offset = 0
    # Separate base offset used only for the DeathLink addresses (see
    # DEATHLINK_RAM_OFFSETS below). The DeathLink struct doesn't shift between
    # NA and PAL by the same 0x1000 as the general save-block (`ram_offset`
    # above) -- it shifts by 0x480 -- so it needs its own per-region base
    deathlink_ram_offset = 0
    # Region-specific dream-battle-detect values Defaults to NA; validate_rom() overwrites these once the region
    # is actually known.
    death_link_dream_val = 68
    death_link_real_val = 84
    prev_data = 0
    prev_shop = 0
    shop_on = False
    receive_buffer = 0
    current_items_received = 0
    prev_check_len = 0
    file_loaded_flag = False
    file_loaded_time = None
    shop_debug_counter = 0
    shop_sent_locations = set()
    block_sent_locations = set()
    ap_was_connected = False


    death_link_prev_mario_alive = None
    death_link_prev_luigi_alive = None
    death_link_prev_gameover = None


    death_link_pending_wear_revert_mario = None
    death_link_pending_wear_revert_luigi = None


    death_link_armed_this_encounter_mario = False
    death_link_armed_this_encounter_luigi = False


    death_link_battle_entered_time = None
    _death_link_was_in_battle = False

    def reset_state(self):
        """Clear watcher memory snapshots so reconnects start from a fresh game state.

        The game reinitializes its shop and block state when Azahar is relaunched,
        but the client keeps the same Python object alive while the emulator is
        closed and reopened. Without resetting the caches, the old shop bytes and
        enable flag make the client believe the shop layout is still valid even
        though the emulator has fully restarted.
        """
        self.prev_data = 0
        self.prev_shop = 0
        self.shop_on = False
        self.receive_buffer = 0
        self.current_items_received = 0
        self.prev_check_len = 0
        self.file_loaded_flag = False
        self.file_loaded_time = None
        self.shop_debug_counter = 0
        self.shop_sent_locations = set()
        self.block_sent_locations = set()
        self.death_link_prev_mario_alive = None
        self.death_link_prev_luigi_alive = None
        self.death_link_prev_gameover = None
        self.death_link_pending_wear_revert_mario = None
        self.death_link_pending_wear_revert_luigi = None
        self.death_link_armed_this_encounter_mario = False
        self.death_link_armed_this_encounter_luigi = False
        self.death_link_battle_entered_time = None
        self._death_link_was_in_battle = False
        self._death_link_addrs_logged = False


    location_names = [403, 505, 506, 507, 508, 510, 511, 2, 3, 4, 5, 6, 7, 8, 9, 1, 12, 10, 13, 11, 14, 15, 16, 17, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 121, 122, 123, 124, 125, 343, 344, 345, 512, 346,
                                347, 348, 513, 701, 705, 601, 401, 402, 404, 405, 406, 407, 408, 461, 462, 463, 501, 502, 503, 504, 509, 531, 514, 515, 516, 517, 409, 410, 411, 465, 466, 467, 412, 413, 414, 415, 468, 469, 470, 471, 416,
                                417, 418, 419, 472, 518, 519, 602, 520, 521, 522, 523, 524, 532, 533, 534, 535, 420, 421, 603, 604, 422, 473, 474, 475, 476, 526, 527, 528, 529, 530, 460, 481, 426, -1, 427, -1, 428, -1, 429, -1, 431, -1, 432,
                                -1, 434, 436, -1, 708, 714, 717, 718, 723, 724, 425, 438, 439, -1, 441, 445, 446, 448, 454, -1, -1, 452, 449, -1, -1, -1, 442, 113, 114, 115, -1, 116, 117, 118, 119, 120, 301, -1, 302, 303, -1, 304, -1, 305, -1, 306,
                                -1, 307, -1, 430, 433, 435, 440, 443, 309, 310, 311, 312, 313, 314, -1, 315, -1, 316, -1, 317, -1, 318, -1, 319, -1, 320, -1, 321, -1, 322, -1, 323, -1, 324, -1, 325, -1, 326, -1, 327, -1, 328, -1, 329, -1, 330, -1, 331,
                                -1, 332, -1, 333, -1, 334, -1, 335, -1, 336, 1220, 337, 338, 339, 340, 1224, 1301, 1303, 1307, 1014, 1016, 341, 342, -1, -1, -1, -1, -1, -1, 641, 648, 803, 624, 625, 626, 763, 731, 804, 805, 839, 840, 650, 630, 631,
                                649, 627, 628, 752, 753, 702, 703, 704, 754, 706, 707, 642, 2115, 643, 605, 606, 607, 756, 757, 709, 710, 711, 712, 713, 758, 715, 759, 760, 761, 770, 771, 772, 749, 750, 751, 719, 720, 721, 722, 762,
                                725, 726, 727, 728, 729, 801, 802, 742, 743, 841, 831, 837, 838, -1, 2116, 832, 833, 835, 836, 764, 765, 766, 767, 768, 769, 744, 745, 746, 747, 748, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 632, 633, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 736, -1, 732, 447, 901, 903, 904, 906, 907, 608, 912, 733, 734, 735, 737, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, 1601, 1602, 1605, 738, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 809, 810, 920, 924, 618, 1612, 1616, 1617, 621, 629, 1203, 813, 1205, 1208, 1209, 1212, 1219,
                                814, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 815, 816, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 821, 822, -1, -1, -1, -1, -1, -1, -1, 825, 826, 827, 828, 829, 830, 739, 740, 741, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 948, 949, 1007, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1015, -1, -1, 1017, 1018,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1020, 1021, 1022, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1024, 1025, 1026, 1027, 1028, 1029,
                                950, 951, -1, -1, 952, 1023, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 203, 204, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1232, 1233, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1235, 1236, 1237, 1238, 1239, 1405, 1406, 1501, 1553, 1502, 1503, 1504, 1505, 1506, 1507, 1509, 1510, 1511, 1514, 1515, 1516, 1517,
                                -1, -1, 1521, 1522, 1523, 1525, 1526, 1528, 1529, 1530, 1531, -1, -1, -1, -1, -1, -1, -1, -1, 1534, 1536, -1, -1, -1, -1, -1, -1, 1538, 1539, -1, -1, 1540, 1541, 1542, 1543, 755, 1545, 1546, 1547, -1, -1, -1, 1548, 1549, -1,
                                -1, -1, -1, -1, -1, 1550, 1551, 1323, 843, 646, 1324, 1240, 1241, 1242, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1243, 1244, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1712, 1713, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1720, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, 1701, -1, -1, -1, -1, -1, -1, 1702, 1703, 1704, -1, -1, -1, -1, -1, -1, 1706, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1709, 1710, -1, -1, -1, -1, 1714, 1715, 1716, -1, -1, -1, 1721, -1, -1, -1, 1722, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, 1725, 1726, 1727, -1, -1, -1, -1, -1, -1, -1, 1728, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 635, 636, 637, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 639, 640, 1623, 1624, 1625, 1626, -1, -1, -1, -1, -1, 1627, 1628, -1, -1, -1, -1, 946, 947, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 455, 456, 457, 458, 479, 453, 477, 478, 902, 954, 1031, 955, 956, 905, 957, 958, 908, 909, 910, 911, 953, 913,
                                914, 915, 916, 917, 918, 1001, 1002, 1003, 1004, 1005, 1006, 919, 921, 922, 923, 614, 615, 616, 1225, 619, 645, 609, 610, 611, 644, 612, 613, 1613, 1614, 1631, 1615, 1618, 1619, 1633, 1606, 622, 623, 647,
                                1607, 1608, 1609, 1610, 1611, 1629, 1630, 1101, 1102, 1103, 1201, 1202, 1204, 1245, 1246, 1206, 1207, 1247, 1210, 1249, 1211, 1213, 1214, 1215, 1216, 1250, 1217, 1251, 1252, 1221, 1222, 1223, 1226, 1227,
                                1253, 1254, 1302, 1304, 1305, 1325, 1401, 1326, 1306, 1308, 1309, 1311, 1312, 1329, 1313, 1402, 1314, 1315, 1330, 1408, 1409, 1230, -1, 1231, 1317, 1319, 1320, 1321, 1332, 1333, 2101, 2102, 2103, 2104,
                                2106, 2108, 2111, 2112, 2113, 2144, 2145, 2146, 2117, 308, -1, -1, 2201, 2202, 2239, 2240, -1, 2209, 2210, 2225, 2226, 2214, 2215, 2216, 2217, 2241, 2242, 2218, 2243, 2221, 2222, 2301, 2302, 2303, 2317, 2318,
                                2304, 2305, 2306, 2307, 2308, 2309, 2321, 2322, 2323, 2324, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1404, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1403, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1519, 1520, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1552, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1919, 1920, 1921, 1922, 1923, 1924, 1925, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1926, 1927, 1928, -1, -1, -1, -1, -1, 1929, 1930, 1931, 1932, 2007, 2008, 2009, 2010, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2021,
                                -1, -1, -1, 2022, 2025, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 2026, 2027, 2028, 2030, -1, -1, -1, 2032, 2033, 2036, 2037, 2038, 2039, -1, -1, 2041, 2042, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 2001, -1, -1,
                                -1, 1815, 1816, 1817, 1818, 1933, 1934, 1935, 459, 480, 1801, 1802, 1821, 1803, 1804, 1805, 1806, 1822, 1807, 1808, 1809, 1811, 1823, 1824, 1813, 1901, 1903, 1904, 1936, 1905, 1906, 1907, 1908, 1937, 1938,
                                1909, 1911, 1913, 1914, 1939, 1940, 1916, 1917, 1941, 2003, 2004, 2005, 2006, 2044, 2045, 2046, 2047, 2048, 2049, 2125, 2126, 2127, 2128, 2129, 2130, 2131, 2132, 2133, 2134, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 2135, 2136, 2137, 2138, 2139, 2140, 2141, 2142, 2143, 2231, -1,
                                -1, 2232, 2233, 2234, 2235, 1228, 2237, -1, -1, -1, -1, -1, -1, -1, -1, -1, 2238, 2310, 2311, -1, -1, -1, -1, -1, -1, 2312, -1, -1, -1, -1, -1, 2313, 2314, 2315, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, 2401, 2402, 2403, 2404, 2405, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 2407, 2408, 2409, 1256, 2211, 2212, -1, -1, -1, -1, -1, -1, -1, 1316, 806, 807, 808, 811, 812, 817, 818, 819, 820, 1620,
                                1705, 823, 824, 201, 202, 205, 1322, 1008, 1009, 1010, 1011, 1012, 1013, 842, 1603, 1604, 1229, 1255, 1819, 1820, 1032, 1033, 1034, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 2316, 2031, 2230, 2236, -1,
                                1327, 1328, 1331, 1407, 2118, 2119, 2120, 2121, 2122, 2227, 2228, -1, -1, -1, 716, 730, 1310, 2229, 2219, 2220, 2244, 2223, 2224, 2406, 349, 126, 127, 128, 129, 464, 525, 423, 424, 437, 444, 450, 451, 834,
                                1544, 617, 620, 1632, 1634, 1248, 1218, 1318, 2205, 2206, 2207, 2319, 2320, 1942, 1943, 1019, 634, 2105, 2107, 2109, 2110, 2114, 2123, 2124, 2203, 2204, 2208, 2213, 1707, 1708, 1711, 1717, 1718, 1719,
                                1723, 1724, 1621, 638, 1622, 1810, 1812, 1814, 1902, 2002, 1910, 1912, 1915, 1918, 1234, 1508, 1512, 1513, 1518, 1524, 1527, 1532, 1533, 1535, 1537, 1554, 2011, 2019, 2020, 2023, 2024, 2029, 2034, 2035,
                                2040, 2043, 1030, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, ]

    async def validate_rom(self, ctx) -> bool:
        """Read the ROM header through the Azahar adapter directly.

        This is intentionally a low-friction sanity check: if Azahar returns zeroed
        memory, we still keep the known-good Dream Team base and continue. The
        goal is a working client, not a perfect BizHawk-compatible ROM validator.
        """
        print("StandaloneMLDTClient: validating ROM via Azahar adapter")
        #logger.info("StandaloneMLDTClient: validating ROM via Azahar adapter")
        try:
            probe_addr = 0x100000
            #print(f"StandaloneMLDTClient.validate_rom: reading System Bus at {probe_addr:#x}")
            #logger.info("StandaloneMLDTClient.validate_rom: reading System Bus at %#x", probe_addr)
            rom_info = await ctx.interface.read(probe_addr, 256)
            print(f"StandaloneMLDTClient.validate_rom: rom_info_len={len(rom_info)} first64={rom_info[:64].hex()}")
            #logger.info("StandaloneMLDTClient.validate_rom: System Bus bytes=%s", rom_info[:16].hex())
            #logger.info("StandaloneMLDTClient.validate_rom: rom_info_len=%d first64=%s", len(rom_info), rom_info[:64].hex())


            na_variant_1 = bytes.fromhex('07 00 00 EB 2A 10 00 EB 57 12 00 EB 45 10 00 EB 65 02 00 FA 19 10 00 EB 3A 10 00 EB 5D 0F 00 EB 5A 0F 00 EA 14 00 9F E5 14 10 9F E5 00 20 A0 E3 01 00 50 E1 04 20 80 34 FC FF FF 3A 1E FF 2F E1 A8 14 6E 00 1C 21 71 00 7C B5 15 00 0C 00 1A 00 00 29 00 90 02 D0 61 00 08 18 80 1E 0B 4B 7B 44 69 46 01 90 28 00 00 F0 BE F8 05 00 00 2C 06 D0 69 46 01 98 80 1C 01 90 00 20 00 F0 C7 F8 A5 42 02 D3 00 20 C0 43 7C BD 28 00 7C BD AB 01 00 00 00 21 01 E0 49 1C 80 1C 02 88 00 2A FA D1 08 00 70 47 FF FF 70 47 C0 46 01 C0 8F E2 1C FF 2F E1 F7 B5 00 26 75 29 10 68 00 99 14 A5 11 D0 FD F1 23 FF 00 28 02 DA 40 42 11 A5 08 E0 00 99 09 68 8A 07 01 D5 0F A5 02 E0 49 07 04 D5 0E A5 01 26 01 E0 FD F1 1C FF 00 9F 00 24 24 37 04 E0 FD F1 22 EF 30 31 39 55 64 1C 00 28 F8 D1 00 98 33 00')
            na_variant_2 = bytes.fromhex('07 00 00 EB 2A 10 00 EB 57 12 00 EB 45 10 00 EB 65 02 00 FA 19 10 00 EB 3A 10 00 EB 5D 0F 00 EB 5A 0F 00 EA 14 00 9F E5 14 10 9F E5 00 20 A0 E3 01 00 50 E1 04 20 80 34 FC FF FF 3A 1E FF 2F E1 A8 14 6E 00 24 21 71 00 7C B5 15 00 0C 00 1A 00 00 29 00 90 02 D0 61 00 08 18 80 1E 0B 4B 7B 44 69 46 01 90 28 00 00 F0 BE F8 05 00 00 2C 06 D0 69 46 01 98 80 1C 01 90 00 20 00 F0 C7 F8 A5 42 02 D3 00 20 C0 43 7C BD 28 00 7C BD AB 01 00 00 00 21 01 E0 49 1C 80 1C 02 88 00 2A FA D1 08 00 70 47 FF FF 70 47 C0 46 01 C0 8F E2 1C FF 2F E1 F7 B5 00 26 75 29 10 68 00 99 14 A5 11 D0 FD F1 09 FF 00 28 02 DA 40 42 11 A5 08 E0 00 99 09 68 8A 07 01 D5 0F A5 02 E0 49 07 04 D5 0E A5 01 26 01 E0 FD F1 02 FF 00 9F 00 24 24 37 04 E0 FD F1 08 EF 30 31 39 55 64 1C 00 28 F8 D1 00 98 33 00')
            pal_variant_1 = bytes.fromhex('07 00 00 EB 2A 10 00 EB 57 12 00 EB 45 10 00 EB 65 02 00 FA 19 10 00 EB 3A 10 00 EB 5D 0F 00 EB 5A 0F 00 EA 14 00 9F E5 14 10 9F E5 00 20 A0 E3 01 00 50 E1 04 20 80 34 FC FF FF 3A 1E FF 2F E1 A8 24 6E 00 1C 31 71 00 7C B5 15 00 0C 00 1A 00 00 29 00 90 02 D0 61 00 08 18 80 1E 0B 4B 7B 44 69 46 01 90 28 00 00 F0 BE F8 05 00 00 2C 06 D0 69 46 01 98 80 1C 01 90 00 20 00 F0 C7 F8 A5 42 02 D3 00 20 C0 43 7C BD 28 00 7C BD AB 01 00 00 00 21 01 E0 49 1C 80 1C 02 88 00 2A FA D1 08 00 70 47 FF FF 70 47 C0 46 01 C0 8F E2 1C FF 2F E1 F7 B5 00 26 75 29 10 68 00 99 14 A5 11 D0 FD F1 FB FE 00 28 02 DA 40 42 11 A5 08 E0 00 99 09 68 8A 07 01 D5 0F A5 02 E0 49 07 04 D5 0E A5 01 26 01 E0 FD F1 F4 FE 00 9F 00 24 24 37 04 E0 FD F1 FA EE 30 31 39 55 64 1C 00 28 F8 D1 00 98 33 00')

            na_offset = AZAHAR_RAM_OFFSETS[TITLE_IDS["E"]]
            pal_offset = AZAHAR_RAM_OFFSETS[TITLE_IDS["P"]]
            detected_title_id = getattr(ctx, "title_id", TITLE_IDS["E"])
            fallback_offset = AZAHAR_RAM_OFFSETS.get(detected_title_id, na_offset)

            na_deathlink_offset = DEATHLINK_RAM_OFFSETS[TITLE_IDS["E"]]
            pal_deathlink_offset = DEATHLINK_RAM_OFFSETS[TITLE_IDS["P"]]
            fallback_deathlink_offset = DEATHLINK_RAM_OFFSETS.get(detected_title_id, na_deathlink_offset)

            na_dream_val, na_real_val = DEATHLINK_BATTLE_VALUES[TITLE_IDS["E"]]
            pal_dream_val, pal_real_val = DEATHLINK_BATTLE_VALUES[TITLE_IDS["P"]]
            fallback_dream_val, fallback_real_val = DEATHLINK_BATTLE_VALUES.get(detected_title_id, (na_dream_val, na_real_val))


            if rom_info in (na_variant_1, na_variant_2):
                self.ram_offset = fallback_offset
                self.deathlink_ram_offset = fallback_deathlink_offset
                self.death_link_dream_val = fallback_dream_val
                self.death_link_real_val = fallback_real_val
                #logger.info("StandaloneMLDTClient.validate_rom: matched NA ROM header -> ram_offset=%#x", self.ram_offset)
                print(f"StandaloneMLDTClient.validate_rom: matched NA ROM header -> ram_offset={self.ram_offset} deathlink_ram_offset={self.deathlink_ram_offset}")
            elif rom_info == pal_variant_1:
                self.ram_offset = pal_offset
                self.deathlink_ram_offset = pal_deathlink_offset
                self.death_link_dream_val = pal_dream_val
                self.death_link_real_val = pal_real_val
                #logger.info("StandaloneMLDTClient.validate_rom: matched PAL ROM header -> ram_offset=%#x", self.ram_offset)
                print(f"StandaloneMLDTClient.validate_rom: matched PAL ROM header -> ram_offset={self.ram_offset} deathlink_ram_offset={self.deathlink_ram_offset}")
            else:
                print(f"StandaloneMLDTClient.validate_rom: ROM header did not match known MLDT signatures; defaulting to NA; first64={rom_info[:64].hex()}")
                #logger.warning("StandaloneMLDTClient.validate_rom: ROM header did not match known MLDT signatures; defaulting to NA; first64=%s", rom_info[:64].hex())
                self.ram_offset = na_offset
                self.deathlink_ram_offset = na_deathlink_offset
                self.death_link_dream_val = na_dream_val
                self.death_link_real_val = na_real_val
                #logger.warning("StandaloneMLDTClient.validate_rom: using MLDT fallback ram_offset=%#x", self.ram_offset)
        except Exception as e:
            print(f"Standalone validate_rom: adapter read failed: {e!r}")
            logger.warning("Standalone validate_rom: adapter read failed: %s", e)
            logger.debug("Standalone validate_rom: adapter read failed", exc_info=True)
            fallback_title_id = getattr(ctx, "title_id", TITLE_IDS["E"])
            self.ram_offset = AZAHAR_RAM_OFFSETS.get(fallback_title_id, AZAHAR_RAM_OFFSETS[TITLE_IDS["E"]])
            self.deathlink_ram_offset = DEATHLINK_RAM_OFFSETS.get(fallback_title_id, DEATHLINK_RAM_OFFSETS[TITLE_IDS["E"]])
            self.death_link_dream_val, self.death_link_real_val = DEATHLINK_BATTLE_VALUES.get(
                fallback_title_id, DEATHLINK_BATTLE_VALUES[TITLE_IDS["E"]])
            #logger.warning("StandaloneMLDTClient.validate_rom: using MLDT fallback ram_offset=%#x after exception", self.ram_offset)

        ctx.game = "Mario and Luigi Dream Team"
        ctx.items_handling = 0b001
        ctx.want_slot_data = True
        return True

    async def process_deathlink(self, ctx, azahar_ram_offset: int) -> None:
        """Poll Mario/Luigi's alive state to send DeathLinks out, and apply any DeathLink
        that was received from another player
        Killing a bro on a received DeathLink isn't instant: a few seconds after he enters a
        battle, we force "hero wear" onto him and push his turn count to the kill threshold,
        and the game itself applies the kill on his next turn. If he flees or wins the battle
        before that happens, the kill is still owed and gets re-armed the next time he enters
        a battle. A death is only ever treated as real -- for confirming a kill has landed, or
        for detecting one to send out -- once both his dead flag AND his HP read 0; a flag flip
        with HP intact (e.g. right after fleeing) doesn't count. Once a kill lands, we restore
        whatever he had equipped before and make sure that death doesn't get echoed back out as
        a new DeathLink to send.
        Called every watcher pass while DeathLink is enabled and a save is loaded.
        """
        dream_battle_addr = azahar_ram_offset + DEATHLINK_DREAM_BATTLE_OFFSET
        mario_dead_addr = azahar_ram_offset + DEATHLINK_MARIO_DEAD_OFFSET
        luigi_dead_addr = azahar_ram_offset + DEATHLINK_LUIGI_DEAD_OFFSET
        mario_wear_addr = azahar_ram_offset + DEATHLINK_MARIO_WEAR_OFFSET
        luigi_wear_addr = azahar_ram_offset + DEATHLINK_LUIGI_WEAR_OFFSET
        mario_turn_addr = azahar_ram_offset + DEATHLINK_MARIO_TURN_OFFSET
        luigi_turn_addr = azahar_ram_offset + DEATHLINK_LUIGI_TURN_OFFSET
        mario_hp_addr = azahar_ram_offset + DEATHLINK_MARIO_HP_OFFSET
        luigi_hp_addr = azahar_ram_offset + DEATHLINK_LUIGI_HP_OFFSET


        if not getattr(self, "_death_link_addrs_logged", False):
            print(f"DeathLink addresses (ram_offset={azahar_ram_offset:#x}): "
                  f"dream_battle={dream_battle_addr:#x} "
                  f"mario_dead={mario_dead_addr:#x} luigi_dead={luigi_dead_addr:#x} "
                  f"mario_wear={mario_wear_addr:#x} luigi_wear={luigi_wear_addr:#x} "
                  f"mario_turn={mario_turn_addr:#x} luigi_turn={luigi_turn_addr:#x} "
                  f"mario_hp={mario_hp_addr:#x} luigi_hp={luigi_hp_addr:#x}")
            self._death_link_addrs_logged = True

        dream_battle_val = int.from_bytes(await ctx.interface.read(dream_battle_addr, 1), byteorder='little')
        if ctx.death_link_debug:
            logger.info(f"DeathLink debug: dream_battle_val={dream_battle_val}")
        if dream_battle_val not in (0, self.death_link_dream_val, self.death_link_real_val):
            if ctx.death_link_debug:
                logger.info(f"DeathLink debug: unrecognized dream_battle_val={dream_battle_val}, skipping pass")
            return  # unrecognized battle state; ignore this pass per spec
        in_dream_battle = dream_battle_val == self.death_link_dream_val
        in_battle = dream_battle_val != 0

        mario_dead_flag = int.from_bytes(await ctx.interface.read(mario_dead_addr, 1), byteorder='little') == 0
        mario_hp = int.from_bytes(await ctx.interface.read(mario_hp_addr, 2), byteorder='little')
        # A death-flag flip alone isn't trustworthy -- fleeing a battle can trip it
        # momentarily even though the bro is fine. Only treat him as dead once both the
        # flag says so *and* his HP has actually hit 0.
        mario_alive = not (mario_dead_flag and mario_hp == 0)
        if in_dream_battle:
            luigi_alive = None
        else:
            luigi_dead_flag = int.from_bytes(await ctx.interface.read(luigi_dead_addr, 1), byteorder='little') == 0
            luigi_hp = int.from_bytes(await ctx.interface.read(luigi_hp_addr, 2), byteorder='little')
            luigi_alive = not (luigi_dead_flag and luigi_hp == 0)

        # Track when the current battle started, so the arm step below can hold off
        # writing wear/turn for a few seconds after a battle begins.
        if not in_battle:
            self.death_link_battle_entered_time = None
        elif not self._death_link_was_in_battle:
            self.death_link_battle_entered_time = time.monotonic()
        self._death_link_was_in_battle = in_battle

        # Not in a battle right now -- clear the "armed this encounter" flags so a kill
        # still in flight gets re-armed as soon as the next battle starts, instead of
        # staying stuck forever if the bro fled or won before their turn came up.
        if not in_battle:
            self.death_link_armed_this_encounter_mario = False
            self.death_link_armed_this_encounter_luigi = False

        # Resolve any kill(s) we triggered on an earlier pass, now that they've landed 
        mario_kill_just_landed = False
        luigi_kill_just_landed = False
        if self.death_link_pending_wear_revert_mario is not None and not mario_alive:
            await ctx.interface.write(mario_wear_addr, bytes([self.death_link_pending_wear_revert_mario]))
            self.death_link_pending_wear_revert_mario = None
            self.death_link_armed_this_encounter_mario = False
            mario_kill_just_landed = True
            #logger.info("DeathLink: Mario's triggered kill landed -- restored his equipment.")
        if not in_dream_battle and self.death_link_pending_wear_revert_luigi is not None and luigi_alive is False:
            await ctx.interface.write(luigi_wear_addr, bytes([self.death_link_pending_wear_revert_luigi]))
            self.death_link_pending_wear_revert_luigi = None
            self.death_link_armed_this_encounter_luigi = False
            luigi_kill_just_landed = True
            #logger.info("DeathLink: Luigi's triggered kill landed -- restored his equipment.")

        if ctx.death_link_debug:
            logger.info(f"DeathLink debug: mode={ctx.death_link_mode} in_dream_battle={in_dream_battle} "
                        f"mario_alive={mario_alive} luigi_alive={luigi_alive} "
                        f"pending_kill={ctx.pending_deathlink_kill} "
                        f"pending_revert_mario={self.death_link_pending_wear_revert_mario} "
                        f"pending_revert_luigi={self.death_link_pending_wear_revert_luigi} "
                        f"prev_mario_alive={self.death_link_prev_mario_alive} "
                        f"prev_luigi_alive={self.death_link_prev_luigi_alive} "
                        f"prev_gameover={self.death_link_prev_gameover}")

        # Receive: mark a kill as owed for the appropriate bro
        if ctx.pending_deathlink_kill:
            await self._apply_deathlink_kill(ctx, in_dream_battle, mario_alive, luigi_alive, mario_wear_addr, luigi_wear_addr)
            ctx.pending_deathlink_kill = False


        battle_settled = (
            self.death_link_battle_entered_time is not None
            and (time.monotonic() - self.death_link_battle_entered_time) >= DEATHLINK_ARM_DELAY_SECONDS
        )
        if self.death_link_pending_wear_revert_mario is not None and mario_alive and in_battle \
                and battle_settled and not self.death_link_armed_this_encounter_mario:
            await ctx.interface.write(mario_wear_addr, bytes([DEATHLINK_HERO_WEAR_VALUE]))
            await ctx.interface.write(mario_turn_addr, bytes([DEATHLINK_KILL_TURN_COUNT]))
            self.death_link_armed_this_encounter_mario = True
            if ctx.death_link_debug:
                logger.info("DeathLink debug: (re-)armed Mario's kill for this battle")
        if not in_dream_battle and self.death_link_pending_wear_revert_luigi is not None and luigi_alive and in_battle \
                and battle_settled and not self.death_link_armed_this_encounter_luigi:
            await ctx.interface.write(luigi_wear_addr, bytes([DEATHLINK_HERO_WEAR_VALUE]))
            await ctx.interface.write(luigi_turn_addr, bytes([DEATHLINK_KILL_TURN_COUNT]))
            self.death_link_armed_this_encounter_luigi = True
            if ctx.death_link_debug:
                logger.info("DeathLink debug: (re-)armed Luigi's kill for this battle")

        # detect a fresh death and, if the mode calls for it, send a DeathLink
        is_gameover = (not mario_alive) if in_dream_battle else (not mario_alive and not luigi_alive)

        if self.death_link_prev_mario_alive is not None:
            mario_just_died = self.death_link_prev_mario_alive and not mario_alive
            luigi_just_died = (
                not in_dream_battle
                and self.death_link_prev_luigi_alive
                and not luigi_alive
            )

            if ctx.death_link_mode in ("gameover", "randombro"):
                if is_gameover and not self.death_link_prev_gameover:
                    any_new_death = mario_just_died or luigi_just_died
                    self_caused_only = (
                        (not mario_just_died or mario_kill_just_landed)
                        and (not luigi_just_died or luigi_kill_just_landed)
                    )
                    if any_new_death and self_caused_only:
                        pass  # don't echo a game over we caused ourselves
                    elif not ctx.server or ctx.slot is None:
                        logger.info("DeathLink: game over detected but not connected/authenticated to the "
                                    "AP server yet -- not sending.")
                    else:
                        logger.info("DeathLink: sending -- game over")
                        await ctx.send_death(f"{ctx.player_names.get(ctx.slot, 'Someone')} game overed.")
            elif ctx.death_link_mode == "singlebro":
                # Don't echo back a death we caused ourselves via a received DeathLink.
                if mario_just_died and mario_kill_just_landed:
                    mario_just_died = False
                if luigi_just_died and luigi_kill_just_landed:
                    luigi_just_died = False
                if (mario_just_died or luigi_just_died) and (not ctx.server or ctx.slot is None):
                    logger.info("DeathLink: a bro died but we're not connected/authenticated to the AP server "
                                "yet -- not sending.")
                elif mario_just_died or luigi_just_died:
                    who = "Mario" if mario_just_died else "Luigi"
                    logger.info(f"DeathLink: sending -- {who} died")
                    await ctx.send_death(f"{ctx.player_names.get(ctx.slot, 'Someone')} let {who} die...")

        self.death_link_prev_mario_alive = mario_alive
        if not in_dream_battle:
            self.death_link_prev_luigi_alive = luigi_alive
        self.death_link_prev_gameover = is_gameover

    async def _apply_deathlink_kill(self, ctx, in_dream_battle: bool, mario_alive: bool, luigi_alive,
                                     mario_wear_addr: int, luigi_wear_addr: int) -> None:
        """Mark the appropriate bro(s) as owing a kill for a received DeathLink
        This only decides who owes a kill and records their pre-DeathLink wear so it can be
        restored later -- it does not write the wear/turn-count trigger itself. The "arm" step
        in process_deathlink() does that, every battle, until the kill actually lands.
        """
        mode = ctx.death_link_mode
        kill_mario = False
        kill_luigi = False

        if in_dream_battle:
            kill_mario = True
        elif mode in ("gameover", "singlebro"):
            kill_mario = True
            kill_luigi = True
        elif mode == "randombro":
            mario_available = mario_alive and self.death_link_pending_wear_revert_mario is None
            luigi_available = luigi_alive and self.death_link_pending_wear_revert_luigi is None
            if mario_available and luigi_available:
                kill_mario, kill_luigi = random.choice([(True, False), (False, True)])
            elif mario_available:
                kill_mario = True
            elif luigi_available:
                kill_luigi = True
            # else: both already dead or already have a kill in flight -- nothing to do


        if kill_mario and mario_alive and self.death_link_pending_wear_revert_mario is None:
            original_wear = (await ctx.interface.read(mario_wear_addr, 1))[0]
            self.death_link_pending_wear_revert_mario = original_wear
        else:
            kill_mario = False

        if kill_luigi and not in_dream_battle and luigi_alive and self.death_link_pending_wear_revert_luigi is None:
            original_wear = (await ctx.interface.read(luigi_wear_addr, 1))[0]
            self.death_link_pending_wear_revert_luigi = original_wear
        else:
            kill_luigi = False

        owed = [name for name, k in (("Mario", kill_mario), ("Luigi", kill_luigi)) if k]
        #logger.info(f"DeathLink: received -- kill owed to {' & '.join(owed) if owed else 'nobody (already dead or already in flight)'}")

    async def game_watcher(self, ctx) -> None:
        #logger.info("StandaloneMLDTClient: running MLDT-like watcher")
        try:
            import worlds._bizhawk as bizhawk
        except Exception:
            return

        azahar_ram_offset = self.ram_offset
        azahar_item_write_addr = azahar_ram_offset + 0x43C + 0x51      # 0x6e815d
        azahar_item_count_low = azahar_ram_offset + 0x43C + 0x4D      # 0x6e8159
        azahar_item_count_high = azahar_ram_offset + 0x43C + 0x4E     # 0x6e815a
        azahar_file_loaded_addr = azahar_ram_offset + 0x1             # 0x6e7cd1
        azahar_block_data_addr = azahar_ram_offset + 0xB8             # 0x6e7d88
        azahar_shop_enabled_addr = azahar_ram_offset + 0x278 + 0x1BE  # shop check
        azahar_shop_data_addr = azahar_ram_offset + 0x278 + 0x1A4     # shop data
        azahar_goal_addr = azahar_ram_offset + 0x278 + 0x8C           # goal check

        while not ctx.exit_event.is_set():
            try:
                # If the server connected after the watcher started, authenticate now
                try:
                    if ctx.server is not None and not ctx.server.socket.closed and ctx.auth is None:
                        await ctx.get_username()
                        logger.info("Authenticated with emulator, sending Connect to server")
                        await ctx.send_connect(name=ctx.auth)
                except Exception:
                    logger.debug("Standalone watcher: failed to send Connect", exc_info=True)


                ap_is_connected = getattr(ctx, "slot", None) is not None
                if ap_is_connected and not self.ap_was_connected:
                    #logger.info("(Re)connected to Archipelago server; re-checking for missed location checks")
                    self.shop_sent_locations = set()
                    self.block_sent_locations = set()
                self.ap_was_connected = ap_is_connected


                try:
                    file_load_byte = await ctx.interface.read(azahar_file_loaded_addr, 1)
                    # The save-loaded state is bit 3. Other bits in this byte
                    # can remain set while an existing save is being loaded.
                    file_has_loaded = (int.from_bytes(file_load_byte, byteorder='little') >> 3) % 2
                    if file_has_loaded != self.file_loaded_flag:
                        #.debug("file_has_loaded changed: %s load_byte=%s", file_has_loaded, file_load_byte.hex())
                        if file_has_loaded:
                            # A save was just selected/loaded. Wait a bit so it
                            # has time to finish loading everything properly.
                            self.file_loaded_time = time.time()
                            #logger.info("Save file loaded; waiting %ds before syncing items", FILE_LOAD_SETTLE_DELAY)
                        else:
                            self.file_loaded_time = None
                    self.file_loaded_flag = file_has_loaded
                except Exception:
                    file_has_loaded = 0
                    self.file_loaded_flag = False
                    self.file_loaded_time = None
                    #logger.debug("file_has_loaded read failed", exc_info=True)

                try:
                    game_state_byte = await ctx.interface.read(GAME_STATE_ADDR, 1)
                    game_state = int.from_bytes(game_state_byte, byteorder='little')
                    in_game = (game_state == 20)
                except Exception:
                    in_game = False
                    #logger.debug("game_state read failed", exc_info=True)

                items_ready = bool(
                    file_has_loaded
                    and self.file_loaded_time is not None
                    and (time.time() - self.file_loaded_time) >= FILE_LOAD_SETTLE_DELAY
                )

                if items_ready:
                    try:
                        game_received_count = int.from_bytes(await ctx.interface.read(azahar_item_count_low, 1), byteorder='little') + (
                            int.from_bytes(await ctx.interface.read(azahar_item_count_high, 1), byteorder='little') * 0x100
                        )
                        if game_received_count > self.current_items_received:
                            self.current_items_received = game_received_count
                        elif self.current_items_received > len(ctx.items_received):
                            self.current_items_received = len(ctx.items_received)
                    except Exception:
                        logger.debug("Failed to read game item count for sync", exc_info=True)

                    if self.current_items_received > len(ctx.items_received):
                        self.current_items_received = len(ctx.items_received)
                    #logger.debug("item write check: current_items_received=%s len(items_received)=%s receive_buffer=%s", self.current_items_received, len(ctx.items_received), self.receive_buffer)
                    if self.current_items_received != len(ctx.items_received):
                        new_items = ctx.items_received
                        for n in range(len(new_items) - self.current_items_received):
                            rn = n + self.current_items_received
                            if self.receive_buffer == 0:
                                to_write = 0
                                if new_items[rn].item > 23 and new_items[rn].item < 239:
                                    to_write = new_items[rn].item - 23
                                elif new_items[rn].item < 239:
                                    to_write = new_items[rn].item + 215
                                else:
                                    to_write = new_items[rn].item
                                #logger.debug("Writing item %s -> emulator (to_write=%s)", new_items[rn].item, to_write)
                                #logger.debug("item write targets: addr=%#x count_low=%#x count_high=%#x", azahar_item_write_addr, azahar_item_count_low, azahar_item_count_high)
                                #logger.debug("Attempting write: addr=%#x data=%s", azahar_item_write_addr, bytes([to_write]).hex())
                                # read-before for diagnostics
                                #try:
                                    #before = await ctx.interface.read(azahar_item_write_addr, 1)
                                    #logger.debug("Before write at %#x: %s", azahar_item_write_addr, before.hex())
                                #except Exception:
                                    #logger.debug("Read-before failed", exc_info=True)
                                await ctx.interface.write(azahar_item_write_addr, bytes([to_write]))
                                # verify write by reading back
                                #try:
                                    #read_back = await ctx.interface.read(azahar_item_write_addr, 1)
                                    #logger.info("Wrote %s to %#x, read-back=%s", to_write, azahar_item_write_addr, read_back.hex())
                                #except Exception:
                                    #logger.debug("Read-back failed after write", exc_info=True)
                                self.current_items_received += 1
                                await ctx.interface.write(azahar_item_count_low, bytes([self.current_items_received % 0x100]))
                                await ctx.interface.write(azahar_item_count_high, bytes([self.current_items_received // 0x100]))
                                self.receive_buffer = 2

                    # Handle cooldown / buffer
                    if self.receive_buffer > 0:
                        has_been_reset = int.from_bytes(await ctx.interface.read(azahar_item_write_addr, 1), byteorder='little')
                        if has_been_reset == 0:
                            self.receive_buffer -= 1
                #else:
                    #logger.debug("Save file not yet settled; holding off on item sync")

                if not file_has_loaded and (self.prev_data or self.shop_on):
                    #logger.debug("Emulator/game not loaded; resetting stale block/shop scan state")
                    self.reset_state()

                if file_has_loaded > 0 and in_game:
                    if self.prev_data == 0:
                        self.current_items_received = int.from_bytes(await ctx.interface.read(azahar_item_count_low, 1), byteorder='little') + (
                            int.from_bytes(await ctx.interface.read(azahar_item_count_high, 1), byteorder='little') * 0x100
                        )
                        #logger.info("Initialized current_items_received from emulator: %s", self.current_items_received)

                        # Block data for Pi'illo area at real Azahar address
                        self.prev_data = (await ctx.interface.read(azahar_block_data_addr, int(0xA00/8)))
                        #logger.info("initial block_data at %#x: %s", azahar_block_data_addr, self.prev_data[:32].hex())


                    shop_enabled_byte = await ctx.interface.read(azahar_shop_enabled_addr, 1)
                    shop_enabled = int.from_bytes(shop_enabled_byte, byteorder='little') % 2
                    #logger.debug("shop init: shop_enabled_byte=%s shop_enabled=%s shop_on_before=%s prev_shop=%s", shop_enabled_byte.hex(), shop_enabled, self.shop_on, (self.prev_shop.hex() if isinstance(self.prev_shop, (bytes, bytearray)) else self.prev_shop))
                    if shop_enabled == 1:
                        self.shop_on = True
                        shop_needs_reset = (
                            not isinstance(self.prev_shop, (bytes, bytearray)) or
                            len(self.prev_shop) < 20 or
                            self.prev_data == 0
                        )
                        if shop_needs_reset:
                            self.prev_shop = await ctx.interface.read(azahar_shop_data_addr, 20)
                            #logger.debug("shop init: prev_shop=%s", self.prev_shop.hex())
                    else:
                        #logger.debug("shop init: shop disabled; clearing prev_shop and shop_on")
                        self.shop_on = False
                        self.prev_shop = 0


                if in_game:
                    block_data = await ctx.interface.read(azahar_block_data_addr, int(0xA00/8))
                    #logger.debug("block_data first 32 bytes at %#x: %s", azahar_block_data_addr, block_data[:32].hex())
                    parsed_block_data = list(block_data)
                    parsed_prev_data = list(self.prev_data) if self.prev_data else [0] * len(parsed_block_data)


                    for byte in range(len(parsed_block_data)):
                        if parsed_block_data[byte] == 0:
                            continue
                        for bit in range(8):
                            if (parsed_block_data[byte] >> bit) % 2 == 0:
                                continue
                            location_id = (byte * 8) + bit
                            if location_id >= len(self.location_names):
                                continue
                            location_name_val = self.location_names[location_id]
                            if location_name_val <= -1 or location_name_val in self.block_sent_locations:
                                continue
                            if location_name_val in ctx.missing_locations:
                                #logger.info("Detected offline location check in emulator: location_index=%d -> location_id=%s", location_id, location_name_val)
                                await ctx.check_locations([location_name_val])
                                self.block_sent_locations.add(location_name_val)

                    for b in range(len(parsed_block_data)):
                        if parsed_block_data[b] != parsed_prev_data[b]:
                            for bit in range(8):
                                bit_to_update = (parsed_block_data[b] >> bit) % 2
                                if bit_to_update != (parsed_prev_data[b] >> bit) % 2:
                                    location_id = (b * 8) + bit
                                    if location_id >= len(self.location_names):
                                        continue
                                    location_name_val = self.location_names[location_id]
                                    if location_name_val > -1 and location_name_val not in self.block_sent_locations:
                                        #logger.info("Detected location check in emulator: location_index=%d -> location_id=%s", location_id, location_name_val)
                                        #logger.info("Location address: byte=%d bit=%d prev_byte=%s new_byte=%s", b, bit, format(parsed_prev_data[b], '#04x'), format(parsed_block_data[b], '#04x'))
                                        #logger.info("Full block address: %#x", azahar_block_data_addr)
                                        await ctx.check_locations([location_name_val])
                                        self.block_sent_locations.add(location_name_val)

                    if self.shop_on:
                        parsed_prev_shop = list(self.prev_shop) if self.prev_shop else [0] * 20
                        shop_data = await ctx.interface.read(azahar_shop_data_addr, 20)
                        parsed_shop_data = list(shop_data)


                        for s in range(len(parsed_shop_data)):
                            for bit in range(8):
                                if (parsed_shop_data[s] >> bit) % 2 == 0:
                                    continue
                                location_index = 3000 + (s * 8) + bit + 1
                                if location_index in self.shop_sent_locations:
                                    continue
                                if location_index in ctx.missing_locations:
                                    #logger.debug("Detected offline shop check in emulator: shop_index=%d byte=%d bit=%d", location_index, s, bit)
                                    await ctx.check_locations([location_index])
                                    self.shop_sent_locations.add(location_index)

                        shop_delta = [
                            (idx, parsed_prev_shop[idx], parsed_shop_data[idx])
                            for idx in range(len(parsed_shop_data))
                            if parsed_prev_shop[idx] != parsed_shop_data[idx]
                        ]
                        if shop_delta:
                            #logger.debug("shop bytes changed: prev=%s new=%s deltas=%s", bytes(parsed_prev_shop).hex(), bytes(parsed_shop_data).hex(), shop_delta)
                            self.shop_debug_counter += 1
                        for s in range(len(parsed_shop_data)):
                            if parsed_shop_data[s] != parsed_prev_shop[s]:
                                for bit in range(8):
                                    bit_to_update = (parsed_shop_data[s] >> bit) % 2
                                    if bit_to_update != (parsed_prev_shop[s] >> bit) % 2:
                                        location_index = 3000 + (s * 8) + bit + 1
                                        if location_index in self.shop_sent_locations:
                                            continue
                                        logger.debug("Detected shop check in emulator: shop_index=%d byte=%d bit=%d prev_byte=%s new_byte=%s", location_index, s, bit, format(parsed_prev_shop[s], '#04x'), format(parsed_shop_data[s], '#04x'))
                                        await ctx.check_locations([location_index])
                                        self.shop_sent_locations.add(location_index)
                        #if not shop_delta and self.shop_debug_counter % 20 == 0:
                            #logger.debug("shop debug: shop_on=True, no byte delta detected, prev_shop=%s", bytes(parsed_prev_shop).hex())
                    #else:
                        #logger.debug("shop debug: shop_on=False, skipping shop scan")

                    # update prevs
                    self.prev_data = block_data
                    if self.shop_on:
                        self.prev_shop = shop_data
                #else:
                    #logger.debug("in_game is False (title/menu/giant battle); skipping block/shop scan this pass")

                # report when Dreamy Bowser has been beaten.
                has_goaled = (int.from_bytes(await ctx.interface.read(azahar_goal_addr, 1), byteorder='little') >> 1) % 2
                if not getattr(ctx, "finished_game", False) and has_goaled == 1:
                    #logger.info("Goal reached in emulator, sending CLIENT_GOAL and setting finished_game")
                    await ctx.send_msgs([{
                        "cmd": "StatusUpdate",
                        "status": ClientStatus.CLIENT_GOAL,
                    }])
                    ctx.finished_game = True

                if file_has_loaded and ctx.death_link_mode != "off":
                    try:
                        await self.process_deathlink(ctx, self.deathlink_ram_offset)
                    except ConnectionError:
                        raise
                    except Exception as e:
                        logger.info(f"DeathLink processing error: {e!r}")
                        logger.debug("DeathLink processing error (full traceback)", exc_info=True)

            except ConnectionError:
                logger.warning("Lost connection to game; resetting watch state and waiting for reconnect")
                ctx.interface_connected = False
                try:
                    ctx.interface.disconnect()
                except Exception:
                    pass
                self.reset_state()
                ctx.initial_delay = True
                ctx.connect_notice_shown = False
                raise
            except Exception:
                #logger.debug("StandaloneMLDTClient.game_watcher loop error", exc_info=True)
                ctx.interface_connected = False
                try:
                    ctx.interface.disconnect()
                except Exception:
                    pass
                self.reset_state()
                ctx.initial_delay = True
                ctx.connect_notice_shown = False
                raise
            await asyncio.sleep(0.4)

# TITLE IDs for Dream Team variants (hex strings in patcher)
TITLE_IDS = {
    "E": 0x00040000000D5A00,
    "P": 0x00040000000D9000,
    "J": 0x0004000000060600,
    "K": 0x00040000000FCD00,
}


AZAHAR_RAM_OFFSETS = {
    TITLE_IDS["E"]: 0x6e7cd0,
    TITLE_IDS["P"]: 0x6E8CD0,
}


DEATHLINK_RAM_OFFSETS = {
    TITLE_IDS["E"]: AZAHAR_RAM_OFFSETS[TITLE_IDS["E"]],
    TITLE_IDS["P"]: AZAHAR_RAM_OFFSETS[TITLE_IDS["E"]] + 0x480,
}


DEATHLINK_BATTLE_VALUES = {
    TITLE_IDS["E"]: (68, 84),
    TITLE_IDS["P"]: (196, 212),
}


class MLDTClientContext(CommonContext):
    command_processor = MLDTCommandProcessor
    interface: N3DSAdapter
    interface_connected: bool
    initial_delay: bool
    show_citra_connect_message: bool
    show_triple_connected_message: bool

    def __init__(self, server_address: Optional[str], password: Optional[str]):
        super().__init__(server_address, password)
        self.interface = N3DSAdapter()
        self.interface_connected = False
        self.initial_delay = True
        self.show_citra_connect_message = True
        self.show_triple_connected_message = True
        self.connect_notice_shown = False
        self.title_id = TITLE_IDS["E"]
        # Decouple from CommonContext's class-level mutable `tags` set so DeathLink tag
        # changes on this instance don't leak into other CommonContext instances/classes.
        self.tags = self.tags.copy()
        self.death_link_mode = "off"  # off, gameover, randombro, singlebro -- set via /deathlink
        self.death_link_debug = False  # set via /deathlink debug
        self.pending_deathlink_kill = False  # set by on_deathlink(); consumed by the game watcher

    def on_deathlink(self, data: dict) -> None:
        #logger.info(f"DeathLink: packet received from server (mode={self.death_link_mode}): {data}")
        if self.death_link_mode == "off":
            # Shouldn't normally get here since the DeathLink tag is only set while a
            # mode is active, but guard against a stray/late packet anyway.
            super().on_deathlink(data)
            return
        self.pending_deathlink_kill = True
        super().on_deathlink(data)


async def game_watcher(ctx: MLDTClientContext, title_id, connect_addr: str) -> None:
    """Minimal Azahar Dream Team watcher.

    This client intentionally avoids the BizHawk shim and the full MLDT runtime.
    We connect to the emulator bridge, validate the game process, then use the
    adapter directly for the few reads/writes the game state needs.

    `title_id` may be a single title id (region forced via --title) or a set
    of candidate title ids to auto-detect the running region from.
    """
    global triple_addr, is_3ds
    handler = StandaloneMLDTClient()
    while not ctx.exit_event.is_set():
        try:
            ctx.invalid = False

            if triple_addr == "" and is_3ds:
                ctx.interface_connected = False
                ctx.interface.disconnect()

            if not ctx.interface_connected:
                handler.reset_state()
                if triple_addr != "":
                    if await ctx.interface.connect(triple_addr, title_id):
                        if ctx.show_triple_connected_message:
                            logger.info("3ds connected!")
                        ctx.initial_delay = True
                        is_3ds = True
                        ctx.interface_connected = True
                        ctx.show_citra_connect_message = False
                        ctx.show_triple_connected_message = False
                        detected_title_id = getattr(ctx.interface, "connected_title_id", None)
                        if detected_title_id is not None:
                            ctx.title_id = detected_title_id
                    else:
                        logger.info("Couldn't connect to 3ds.")
                        ctx.interface_connected = False
                        ctx.interface.disconnect()
                        triple_addr = ""
                        continue
                else:
                    ctx.interface.disconnect()
                    ctx.show_triple_connected_message = True
                    is_3ds = False
                    if ctx.show_citra_connect_message:
                        logger.info("Connecting to game...")
                    ctx.show_citra_connect_message = False
                    ctx.interface_connected = False
                    target_addr = connect_addr or "127.0.0.1"
                    if not await ctx.interface.connect(target_addr, title_id):
                        await asyncio.sleep(1)
                        continue
                    ctx.interface_connected = True
                    ctx.initial_delay = True
                    detected_title_id = getattr(ctx.interface, "connected_title_id", None)
                    if detected_title_id is not None:
                        ctx.title_id = detected_title_id
                    logger.info("Emulator connected! (title_id=%#x)", ctx.title_id)

            if ctx.initial_delay:
                delay = 5 if is_3ds else 1
                await asyncio.sleep(delay)
                ctx.initial_delay = False


            await handler.validate_rom(ctx)

            try:
                if ctx.server is not None and not ctx.server.socket.closed and ctx.auth is None:
                    await ctx.get_username()
                    #logger.info("Authenticated with emulator, sending Connect to server")
                    await ctx.send_connect(name=ctx.auth)
            except Exception:
                #logger.debug("Failed to send Connect after ROM validation", exc_info=True)
                pass

            if not ctx.interface_connected:
                continue

            await handler.game_watcher(ctx)

        except ConnectionError:
            logger.warning("Lost connection to game; waiting for emulator to reconnect")
            try:
                ctx.interface.disconnect()
            except Exception:
                pass
            handler.reset_state()
            ctx.interface_connected = False
            ctx.initial_delay = True
            ctx.connect_notice_shown = False
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            logger.warning("Lost connection to game; waiting for emulator to reconnect")
            try:
                ctx.interface.disconnect()
            except Exception:
                pass
            ctx.interface_connected = False
            ctx.initial_delay = True
            ctx.connect_notice_shown = False
            await asyncio.sleep(1)


def launch(*launch_args) -> None:
    async def main():
        parser = get_base_parser()
        parser.add_argument("patch_file", default="", type=str, nargs="?",
                            help="Path to an Archipelago patch file")
        parser.add_argument("--title", default="", type=str,
                            help="Region letter (E=NA, P=PAL, J=JP, K=KR) or an explicit TITLE_ID hex")
        parser.add_argument("--addr", default="127.0.0.1", type=str,
                            help="Emulator connector address (default 127.0.0.1)")
        args = parser.parse_args(launch_args)

        # Determine which title id(s) to connect against.
        # If the user explicitly named a region (or gave a raw hex title id),
        # only match that one. Otherwise auto-detect by accepting any known
        # region and using whichever one is actually running in the emulator.
        connect_title_id = None
        default_title_id = TITLE_IDS.get("E", 0)
        if args.title:
            region_key = args.title.strip().upper()
            if region_key in TITLE_IDS:
                connect_title_id = TITLE_IDS[region_key]
            else:
                try:
                    connect_title_id = int(args.title, 16)
                except Exception:
                    connect_title_id = int(args.title)
            default_title_id = connect_title_id
        else:
            # Auto-detect: accept any known region's title id, and figure out
            # which one actually connected from ctx.interface.connected_title_id.
            connect_title_id = set(TITLE_IDS.values())

        ctx = MLDTClientContext(args.connect, args.password)
        ctx.title_id = default_title_id
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="ServerLoop")

        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        watcher_task = asyncio.create_task(game_watcher(ctx, connect_title_id, args.addr), name="GameWatcher")

        try:
            await watcher_task
        except Exception as e:
            logger.exception(e)

        await ctx.exit_event.wait()
        await ctx.shutdown()

    asyncio.run(main())
