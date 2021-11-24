import argparse

from peo.disasm.disasm import disasm
from peo.fhdr import fhdr
from peo.checksec import checksec
from peo.decompile import decompile


def main():
    parser = argparse.ArgumentParser(
        description="Python Extensions for objdump"
    )
    parser.add_argument("file")  # 必須の引数
    parser.add_argument(
        "-d",
        "--disassemble",
        action="store_true",
        help="Display assembler contents of executable sections"
    )
    parser.add_argument(
        "-f",
        "--file-headers",
        action="store_true",  # フラグ
        help="Display the contents of the overall file header"
    )
    parser.add_argument(
        "-c",
        "--checksec",
        action="store_true",
        help="Display properties of executables"
    )
    parser.add_argument(
        "--decompile",
        action="store_true",
        help="Desplay the decompilation of executable"
    )

    args = parser.parse_args()

    filepath = args.file  # ファイルのパス

    if args.disassemble:
        fcn = input("Do you want to disassemble all functions? (y/N/<fcn_name>): ")
        if fcn.lower() == "y" or fcn == "":
            disasm(filepath)
        elif fcn.upper() == "N":
            pass
        else:
            disasm(filepath, fcn)
    elif args.file_headers:
        fhdr(filepath)
    elif args.checksec:
        checksec(filepath)
    elif args.decompile:
        decompile(filepath)


if __name__ == "__main__":
    main()
