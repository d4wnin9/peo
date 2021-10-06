import subprocess as sp

from peo.util import *
from peo.fhdr import EType


def checksec(filepath):
    RELRO = 0
    SSP = 0
    NX = 0
    PIE = 0

    with open(filepath, "rb") as f:
        buf = f.read(18)
    proc = sp.run(["objdump", "-x", filepath], encoding="utf-8", stdout=sp.PIPE, stderr=sp.PIPE)

    # RELRO
    if "RELRO" in proc.stdout:
        RELRO = 1
        if "BIND" in proc.stdout:
            RELRO = 2

    # SSP
    if "__stack_chk_fail" in proc.stdout:
        SSP = 1
    if "__intel_security_cookie" in proc.stdout:
        SSP = 1

    # NX
    if "STACK" in proc.stdout:
        NX = 1
        if "RWE" in proc.stdout:
            NX = 0

    # PIE
    type = EType(int.from_bytes(buf[16:18], 'little')).name
    if type == "EXEC":
        PIE = 1
    elif type == "DYN":
        if "DEBUG" in proc.stdout:
            PIE = 2
        else:
            PIE = 3
    elif type == "REL":
        PIE = 4


    print("RELRO: ", end="")
    if RELRO == 0:
        print(Color.redify("No RELRO"))
    elif RELRO == 1:
        print(Color.yellowify("Partial RELRO"))
    elif RELRO == 2:
        print(Color.greenify("Full RELRO"))

    print("CANARY: ", end="")
    if SSP == 0:
        print(Color.redify("No canary found"))
    elif SSP == 1:
        print(Color.greenify("Canary found"))

    print("NX: ", end="")
    if NX == 0:
        print(Color.redify("NX disabled"))
    elif NX == 1:
        print(Color.greenify("NX enabled"))

    print("PIE: ", end="")
    if PIE == 0:
        print(Color.highlightify(Color.redify("Not an ELF file")))
    if PIE == 1:
        print(Color.redify("No PIE"))
    elif PIE == 2:
        print(Color.greenify("PIE enabled"))
    elif PIE == 3:
        print(Color.blueify("DSO"))
    elif PIE == 4:
        print(Color.purplify("REL"))