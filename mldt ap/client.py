from typing import TYPE_CHECKING

from NetUtils import ClientStatus

import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient

import logging

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

# IMPORTANT:
# ctx.check_locations can be used to update a location on the server by giving the location name
# Meanwhile, ctx.missing_locations returns an array of every location that hasn't been checked
# Also, ctx.items_received gives a list of every item that's been received

class MLDTClient(BizHawkClient):
    game = "Mario and Luigi Dream Team"
    system = "3DS"
    patch_suffix = ".apworld"
    ram_offset = 0
    prev_data = 0
    location_names = []
    logger = 0
    receive_buffer = 0
    current_items_received = 0
    prev_checked_len = 0

    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        try:
            # Check ROM name/patch version
            rom_info = (await bizhawk.read(ctx.bizhawk_ctx, [(0x100000, 256, "System Bus")]))[0] #Gets the data from Bizhawk's System Bus that corresponds to the first 0x100 bytes in code.bin
            #Checks the code.bin info to see what the current ROM is
            if rom_info == bytes.fromhex('07 00 00 EB 2A 10 00 EB 57 12 00 EB 45 10 00 EB 65 02 00 FA 19 10 00 EB 3A 10 00 EB 5D 0F 00 EB 5A 0F 00 EA 14 00 9F E5 14 10 9F E5 00 20 A0 E3 01 00 50 E1 04 20 80 34 FC FF FF 3A 1E FF 2F E1 A8 14 6E 00 1C 21 71 00 7C B5 15 00 0C 00 1A 00 00 29 00 90 02 D0 61 00 08 18 80 1E 0B 4B 7B 44 69 46 01 90 28 00 00 F0 BE F8 05 00 00 2C 06 D0 69 46 01 98 80 1C 01 90 00 20 00 F0 C7 F8 A5 42 02 D3 00 20 C0 43 7C BD 28 00 7C BD AB 01 00 00 00 21 01 E0 49 1C 80 1C 02 88 00 2A FA D1 08 00 70 47 FF FF 70 47 C0 46 01 C0 8F E2 1C FF 2F E1 F7 B5 00 26 75 29 10 68 00 99 14 A5 11 D0 FD F1 23 FF 00 28 02 DA 40 42 11 A5 08 E0 00 99 09 68 8A 07 01 D5 0F A5 02 E0 49 07 04 D5 0E A5 01 26 01 E0 FD F1 1C FF 00 9F 00 24 24 37 04 E0 FD F1 22 EF 30 31 39 55 64 1C 00 28 F8 D1 00 98 33 00'):
                #North American 1.0 ROM
                self.ram_offset = 0x760BCD0
            elif rom_info == bytes.fromhex('07 00 00 EB 2A 10 00 EB 57 12 00 EB 45 10 00 EB 65 02 00 FA 19 10 00 EB 3A 10 00 EB 5D 0F 00 EB 5A 0F 00 EA 14 00 9F E5 14 10 9F E5 00 20 A0 E3 01 00 50 E1 04 20 80 34 FC FF FF 3A 1E FF 2F E1 A8 14 6E 00 24 21 71 00 7C B5 15 00 0C 00 1A 00 00 29 00 90 02 D0 61 00 08 18 80 1E 0B 4B 7B 44 69 46 01 90 28 00 00 F0 BE F8 05 00 00 2C 06 D0 69 46 01 98 80 1C 01 90 00 20 00 F0 C7 F8 A5 42 02 D3 00 20 C0 43 7C BD 28 00 7C BD AB 01 00 00 00 21 01 E0 49 1C 80 1C 02 88 00 2A FA D1 08 00 70 47 FF FF 70 47 C0 46 01 C0 8F E2 1C FF 2F E1 F7 B5 00 26 75 29 10 68 00 99 14 A5 11 D0 FD F1 09 FF 00 28 02 DA 40 42 11 A5 08 E0 00 99 09 68 8A 07 01 D5 0F A5 02 E0 49 07 04 D5 0E A5 01 26 01 E0 FD F1 02 FF 00 9F 00 24 24 37 04 E0 FD F1 08 EF 30 31 39 55 64 1C 00 28 F8 D1 00 98 33 00'):
                #North American 1.1 ROM
                self.ram_offset = 0x760BCD0
            elif rom_info == bytes.fromhex('07 00 00 EB 2A 10 00 EB 57 12 00 EB 45 10 00 EB 65 02 00 FA 19 10 00 EB 3A 10 00 EB 5D 0F 00 EB 5A 0F 00 EA 14 00 9F E5 14 10 9F E5 00 20 A0 E3 01 00 50 E1 04 20 80 34 FC FF FF 3A 1E FF 2F E1 A8 24 6E 00 1C 31 71 00 7C B5 15 00 0C 00 1A 00 00 29 00 90 02 D0 61 00 08 18 80 1E 0B 4B 7B 44 69 46 01 90 28 00 00 F0 BE F8 05 00 00 2C 06 D0 69 46 01 98 80 1C 01 90 00 20 00 F0 C7 F8 A5 42 02 D3 00 20 C0 43 7C BD 28 00 7C BD AB 01 00 00 00 21 01 E0 49 1C 80 1C 02 88 00 2A FA D1 08 00 70 47 FF FF 70 47 C0 46 01 C0 8F E2 1C FF 2F E1 F7 B5 00 26 75 29 10 68 00 99 14 A5 11 D0 FD F1 FB FE 00 28 02 DA 40 42 11 A5 08 E0 00 99 09 68 8A 07 01 D5 0F A5 02 E0 49 07 04 D5 0E A5 01 26 01 E0 FD F1 F4 FE 00 9F 00 24 24 37 04 E0 FD F1 FA EE 30 31 39 55 64 1C 00 28 F8 D1 00 98 33 00'):
                #PAL 1.0 ROM
                self.ram_offset = 0x760ACD0
            else:
                return False  # Not a MYGAME ROM
        except bizhawk.RequestFailedError:
            return False  # Not able to get a response, say no for now

        # This is a MYGAME ROM
        ctx.game = self.game
        ctx.items_handling = 0b001
        ctx.want_slot_data = True
        self.logger = logging.getLogger("Client")

        #An array of the location ids (it's pretty massive)
        self.location_names = [403, 505, 506, 507, 508, 510, 511, 2, 3, 4, 5, 6, 7, 8, 9, 1, 12, 10, 13, 11, 14, 15, 16, 17, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 121, 122, 123, 124, 125, 343, 344, 345, 512, 346,
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
                                -1, -1, -1, 2022, 2025, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 2026, 2027, 2028, 2030, -1, -1, -1, 2032, 2033, 2036, 2037, 2038, 2039, -1, -1, 2041, 2042, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 2002, -1, -1,
                                -1, 1815, 1816, 1817, 1818, 1933, 1934, 1935, 459, 480, 1801, 1802, 1821, 1803, 1804, 1805, 1806, 1822, 1807, 1808, 1809, 1811, 1823, 1824, 1813, 1901, 1903, 1904, 1936, 1905, 1906, 1907, 1908, 1937, 1938,
                                1909, 1911, 1913, 1914, 1939, 1940, 1916, 1917, 1941, 2003, 2004, 2005, 2006, 2044, 2045, 2046, 2047, 2048, 2049, 2125, 2126, 2127, 2128, 2129, 2130, 2131, 2132, 2133, 2134, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 2135, 2136, 2137, 2138, 2139, 2140, 2141, 2142, 2143, 2231, -1,
                                -1, 2232, 2233, 2234, 2235, 1228, 2237, -1, -1, -1, -1, -1, -1, -1, -1, -1, 2238, 2310, 2311, -1, -1, -1, -1, -1, -1, 2312, -1, -1, -1, -1, -1, 2313, 2314, 2315, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, 2401, 2402, 2403, 2404, 2405, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 2407, 2408, 2409, 1256, 2211, 2212, -1, -1, -1, -1, -1, -1, -1, 1316, 806, 807, 808, 811, 812, 817, 818, 819, 820, 1620,
                                1705, 823, 824, 201, 202, 205, 1322, 1008, 1009, 1010, 1011, 1012, 1013, 842, 1603, 1604, 1229, 1255, 1819, 1820, 1032, 1033, 1034, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 2316, 2031, 2230, 2236, -1,
                                1327, 1328, 1331, 1407, 2118, 2119, 2120, 2121, 2122, 2227, 2228, -1, -1, -1, 716, 730, 1310, 2229, 2219, 2220, 2244, 2223, 2224, 2406, 349, 126, 127, 128, 129, 464, 525, 423, 424, 437, 444, 450, 451, 834,
                                1544, 617, 620, 1632, 1634, 1248, 1218, 1318, 2205, 2206, 2207, 2319, 2320, 1942, 1943, 1019, 634, 2105, 2107, 2109, 2110, 2114, 2123, 2124, 2203, 2204, 2208, 2213, 1707, 1708, 1711, 1717, 1718, 1719,
                                1723, 1724, 1621, 638, 1622, 1810, 1812, 1814, 1902, 2001, 1910, 1912, 1915, 1918, 1234, 1508, 1512, 1513, 1518, 1524, 1527, 1532, 1533, 1535, 1537, 1554, 2011, 2019, 2020, 2023, 2024, 2029, 2034, 2035,
                                2040, 2043, 1030, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, ]

        return True

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        try:
            # Only runs the code if the server is connected and the file has been loaded
            if ctx.server is None or ctx.server.socket.closed or ctx.slot_data is None:
                return
            file_has_loaded = (int.from_bytes((await bizhawk.read(
                            ctx.bizhawk_ctx,
                            [(self.ram_offset + 0x1, 1, "FCRAM")]
                        ))[0], byteorder = 'little') >> 3) % 2
            if file_has_loaded > 0:
                # Sets prev_data only if it hasn't been set before
                if self.prev_data == 0:
                    self.prev_data = (await bizhawk.read(
                    ctx.bizhawk_ctx,
                    [(self.ram_offset + 0xB8, 0xA00/8, "FCRAM")]
                    ))[0]

                    #Since the prev_data hasn't been set yet, it's the first time we booted the application, so we can initialize a few things
                    parsed_prev_data = list(self.prev_data)
                    locations_to_check = []
                    for byte in range(len(parsed_prev_data)):
                        for bit in range(8):
                            #Checks any locations that were set in between play sessions
                            if (parsed_prev_data[byte] >> bit) % 2 == 1:
                                #self.logger.info("Bit set")
                                location_id = (byte*8) + bit
                                if self.location_names[location_id] > -1:
                                    if self.location_names[location_id] in ctx.missing_locations:
                                        locations_to_check.append(self.location_names[location_id])
                                    self.location_names[location_id] = -1
                    await ctx.check_locations(locations_to_check)

                    #Updates the current items to match up with the amount of items that have been received
                    self.current_items_received = int.from_bytes((await bizhawk.read(
                        ctx.bizhawk_ctx,
                        [(self.ram_offset + 0x43C + 0x4D, 2, "FCRAM")]
                    ))[0], byteorder = 'little')

                    self.prev_check_len = len(ctx.checked_locations)

                # Read the block data to check for changes
                block_data = (await bizhawk.read(
                    ctx.bizhawk_ctx,
                    [(self.ram_offset + 0xB8, 0xA00/8, "FCRAM")]
                ))[0]
                parsed_block_data = list(block_data)
                parsed_prev_data = list(self.prev_data)

                # Checks for changes in the block data
                for b in range(len(parsed_block_data)):
                    if parsed_block_data[b] != parsed_prev_data[b]:
                        #self.logger.info("Difference")
                        # If it detects a change, it iterates through that byte until it finds the change
                        for bit in range(8):
                            bit_to_update = (parsed_block_data[b] >> bit) % 2
                            if bit_to_update != (parsed_prev_data[b] >> bit) % 2:
                                #self.logger.info("Bit difference")
                                #Get the location name for this bit, then send the location if it hasn't already been checked
                                location_id = (b*8) + bit
                                if self.location_names[location_id] > -1:
                                    #self.logger.info(ctx.missing_locations)
                                    await ctx.check_locations([self.location_names[location_id]])
                                    self.prev_check_len = len(ctx.checked_locations)
                                    self.location_names[location_id] = -1
                
                #if self.prev_check_len != len(ctx.checked_locations):
                #    #Handles giving an item if it was sent through the client
                #    #self.logger.info("Checking item")
                #    new_items = ctx.checked_locations[-1]
                #    to_write = 0
                #    if new_items.item > 23 and new_items.item < 229:
                #        to_write = new_items.item - 23
                #    elif new_items.item < 229:
                #        to_write = new_items.item + 205
                #    else:
                #        to_write = new_items.item
                #    await bizhawk.write(ctx.bizhawk_ctx, [(self.ram_offset + 0x43C + 0x51, bytes([to_write]), "FCRAM")])
                #    self.receive_buffer = 5

                
                # Handles receiving items
                if self.current_items_received > len(ctx.items_received):
                    self.current_items_received = len(ctx.items_received)
                if self.current_items_received != len(ctx.items_received):
                    #self.logger.info(self.current_items_received)
                    new_items = ctx.items_received
                    #self.logger.info(len(new_items))
                    for n in range(len(new_items) - self.current_items_received):
                        #self.logger.info("Iterate")
                        rn = n + self.current_items_received
                        if self.receive_buffer == 0:
                            #self.logger.info("Checking item")
                            to_write = 0
                            if new_items[rn].item > 23 and new_items[rn].item < 229:
                                to_write = new_items[rn].item - 23
                            elif new_items[rn].item < 229:
                                to_write = new_items[rn].item + 205
                            else:
                                to_write = new_items[rn].item
                            await bizhawk.write(ctx.bizhawk_ctx, [(self.ram_offset + 0x43C + 0x51, bytes([to_write]), "FCRAM")])
                            self.current_items_received += 1
                            await bizhawk.write(ctx.bizhawk_ctx, [(self.ram_offset + 0x43C + 0x4D, 
                                                                bytes([self.current_items_received % 0x100]), "FCRAM")])
                            await bizhawk.write(ctx.bizhawk_ctx, [(self.ram_offset + 0x43C + 0x4E, 
                                                                bytes([self.current_items_received // 0x100]), "FCRAM")])
                            self.receive_buffer = 5
                
                # Handles the cooldown between receiving items
                if self.receive_buffer > 0:
                    has_been_reset = int.from_bytes((await bizhawk.read(
                        ctx.bizhawk_ctx,
                        [(self.ram_offset + 0x43C + 0x51, 1, "FCRAM")]
                    ))[0], byteorder = 'little')
                    if has_been_reset == 0:
                        self.receive_buffer -= 1
                
                # Sets the player status if they have defeated Dreamy Bowser
                has_goaled = (int.from_bytes((await bizhawk.read(
                        ctx.bizhawk_ctx,
                        [(self.ram_offset + 0x278 + 0x8C, 1, "FCRAM")]
                    ))[0], byteorder = 'little') >> 1) % 2
                if not ctx.finished_game and has_goaled == 1:
                    await ctx.send_msgs([{
                        "cmd": "StatusUpdate",
                        "status": ClientStatus.CLIENT_GOAL
                    }])
                    ctx.finished_game = True
                    
                # Updates prev_data to have the data from this frame (which will be the previous next frame)
                self.prev_data = block_data

        except bizhawk.RequestFailedError:
            # The connector didn't respond. Exit handler and return to main loop to reconnect
            pass