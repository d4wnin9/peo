from enum import Enum

from peo.util import Color


class EiClass(Enum):
    NONE = 0x00
    ELF32 = 0x01
    ELF64 = 0x02
    NUM = 0x03


class EiData(Enum):
    NONE = 0x00
    LSB = 0x01
    MSB = 0x02


class EiVersion(Enum):
    NONE = 0x00
    CURRENT = 0x01
    NUM = 0x02


class EiOsAbi(Enum):
    NONE = 0x00
    HPUX = 0x01
    NETBSD = 0x02
    LINUX = 0x03


class EType(Enum):
    NONE = 0x00
    REL = 0x01
    EXEC = 0x02
    DYN = 0x03
    CORE = 0x04
    LOOS = 0xfe00
    HIOS = 0xfeff
    LOPROC = 0xff00
    HIPROC = 0xffff


class EMachine(Enum):
    NONE = 0x00
    M32 = 0x01
    Sparc = 0x02
    I386 = 0x03
    M68K = 0x04
    M88K = 0x05
    I486 = 0x06
    I860 = 0x07
    X64 = 0x3e
    AARCH64 = 0xb7


def fhdr32(buf):
    # 例外処理なくていい......?
    print(f"ELF Header:")
    print(f"  Magic:   {Color.redify(buf[:4].hex()) + buf[4:16].hex()}")
    print(f"  Class:                             {EiClass(buf[4]).name}")
    print(f"  Data:                              {EiData(buf[5]).name}")
    print(f"  Version:                           {EiVersion(buf[6]).name}")
    print(f"  OS/ABI:                            {EiOsAbi(buf[7]).name}")
    print(f"  Type:                              {EType(int.from_bytes(buf[16:18], 'little')).name}")
    print(f"  Machine:                           {EMachine(int.from_bytes(buf[18:20], 'little')).name}")
    print(f"  Entry point address:               0x{buf[24:28][::-1].hex()}")
    print(f"  Start of program headers:          0x{buf[28:32][::-1].hex()} (bytes into file)")
    print(f"  Start of section headers:          0x{buf[32:36][::-1].hex()} (bytes into file)")
    print(f"  Flags:                             0x{buf[36:40][::-1].hex()}")
    print(f"  Size of this header:               0x{buf[40:42][::-1].hex()} (bytes)")
    print(f"  Size of program headers:           0x{buf[42:44][::-1].hex()} (bytes)")
    print(f"  Number of program headers:         0x{buf[44:46][::-1].hex()}")
    print(f"  Size of section headers:           0x{buf[46:48][::-1].hex()} (bytes)")
    print(f"  Number of section headers:         0x{buf[48:50][::-1].hex()}")
    print(f"  Section header string table index: 0x{buf[50:52][::-1].hex()}")


def fhdr64(buf):
    # 例外処理なくていい......?
    print(f"ELF Header:")
    print(f"  Magic:   {Color.redify(buf[:4].hex()) + buf[4:16].hex()}")
    print(f"  Class:                             {EiClass(buf[4]).name}")
    print(f"  Data:                              {EiData(buf[5]).name}")
    print(f"  Version:                           {EiVersion(buf[6]).name}")
    print(f"  OS/ABI:                            {EiOsAbi(buf[7]).name}")
    print(f"  Type:                              {EType(int.from_bytes(buf[16:18], 'little')).name}")
    print(f"  Machine:                           {EMachine(int.from_bytes(buf[18:20], 'little')).name}")
    print(f"  Entry point address:               0x{buf[24:32][::-1].hex()}")
    print(f"  Start of program headers:          0x{buf[32:40][::-1].hex()} (bytes into file)")
    print(f"  Start of section headers:          0x{buf[40:48][::-1].hex()} (bytes into file)")
    print(f"  Flags:                             0x{buf[48:52][::-1].hex()}")
    print(f"  Size of this header:               0x{buf[52:54][::-1].hex()} (bytes)")
    print(f"  Size of program headers:           0x{buf[54:56][::-1].hex()} (bytes)")
    print(f"  Number of program headers:         0x{buf[56:58][::-1].hex()}")
    print(f"  Size of section headers:           0x{buf[58:60][::-1].hex()} (bytes)")
    print(f"  Number of section headers:         0x{buf[60:62][::-1].hex()}")
    print(f"  Section header string table index: 0x{buf[62:64][::-1].hex()}")


def fhdr(filepath):
    with open(filepath, "rb") as f:
        buf = f.read(64)

    try:
        ei_class = EiClass(buf[4]).name
    except ValueError:
        pass
    if ei_class == "ELF32":
        fhdr32(buf)
    elif ei_class == "ELF64":
        fhdr64(buf)
    else:
        print("Only elf32 and elf64 are supported")
