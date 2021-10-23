from typing import List

from peo.util import get_section_as_str


class Comment:
    def __init__(self, filepath: str, msgs: List[List[str]]):
        self.filepath = filepath
        self.msgs = msgs

    def lea_rodata(self):
        for i, msg in enumerate(self.msgs):
            try:
                if "lea" in msg[2]:
                    addr = int(msg[3].split(" ")[0], 16)

                    plain_str = repr(
                        get_section_as_str(self.filepath, '.rodata', addr)
                    )

                    self.msgs[i][3] = f"; {hex(addr)} ; {plain_str}"
            except IndexError:
                pass

    def movabs(self):
        for i, msg in enumerate(self.msgs):
            try:
                if "movabs" in msg[2]:
                    long_str_little = int(msg[2].split(",")[1], 16)

                    plain_str = long_str_little.to_bytes(
                        (long_str_little.bit_length() + 7) // 8,
                        byteorder='little'
                    ).decode('utf-8', 'backslashreplace')

                    self.msgs[i].append(f"; {repr(plain_str)}")
            except IndexError:
                pass

    def mov_word(self):
        for i, msg in enumerate(self.msgs):
            try:
                if "mov" in msg[2] and "ORD" in msg[2].split(" ")[1]:
                    long_str_little = int(msg[2].split(",")[1], 16)

                    plain_str = long_str_little.to_bytes(
                        (long_str_little.bit_length() + 7) // 8,
                        byteorder='little'
                    ).decode('utf-8', 'backslashreplace')

                    self.msgs[i].append(f"; {repr(plain_str)}")
            except IndexError:
                pass
            except ValueError:
                pass

    def add(self) -> List[List[str]]:
        self.lea_rodata()
        self.movabs()
        self.mov_word()

        return self.msgs
