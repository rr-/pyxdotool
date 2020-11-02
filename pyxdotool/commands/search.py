import argparse
from enum import Enum

from pyxdotool.commands.base import BaseCommand, CommandContext


class WindowSearchMode(Enum):
    Any = 1
    All = 2


class SearchWindowCommand(BaseCommand):
    names = ["search"]
    description = "If none of --name, --classname, or --class are specified, the defaults are: --name --classname --class"

    @classmethod
    def decorate_arg_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("regexp")
        parser.add_argument("--class", action="store_true")
        parser.add_argument("--classname", action="store_true")
        parser.add_argument("--maxdepth", type=int, metavar="N")
        parser.add_argument("--onlyvisible", action="store_true")
        parser.add_argument("--pid", type=int)
        parser.add_argument("--screen", type=int, metavar="N")
        parser.add_argument("--desktop", type=int, metavar="N")
        parser.add_argument("--limit", type=int, metavar="N")
        parser.add_argument("--name", action="store_true")
        parser.add_argument("--shell", action="store_true")
        parser.add_argument("--prefix", metavar="STR")
        parser.add_argument("--title", action="store_true")
        parser.add_argument(
            "--all", action="store_const", const=WindowSearchMode.Any
        )
        parser.add_argument(
            "--any", action="store_const", const=WindowSearchMode.All
        )
        parser.add_argument("--sync", action="store_true")

    @classmethod
    def run(cls, ctx: CommandContext) -> None:
        pass
