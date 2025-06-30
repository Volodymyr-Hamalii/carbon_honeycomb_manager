import sys


class CommandLineArgsHandler:
    @staticmethod
    def get_str_arg(index: int, default: str) -> str:
        return sys.argv[index] if len(sys.argv) > index and sys.argv[index] != "_" else default

    @staticmethod
    def get_bool_arg(index: int, to_compare: str, default: bool) -> bool:
        return sys.argv[index] == to_compare if len(sys.argv) > index and sys.argv[index] != "_" else default
