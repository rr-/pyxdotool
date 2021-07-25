import argparse
from dataclasses import dataclass

from pyxdotool.xdo import Xdo


@dataclass
class CommandContext:
    xdo: Xdo
    args: argparse.Namespace
    window_stack: list[int]


class BaseCommand:
    names: list[str] = NotImplemented
    description: str = NotImplemented

    @classmethod
    def run(cls, ctx: CommandContext) -> None:
        raise NotImplementedError("not implemented")

    @classmethod
    def decorate_arg_parser(cls, parser: argparse.ArgumentParser) -> None:
        pass
