import argparse
import typing as T
from dataclasses import dataclass

from pyxdotool.xdo import Xdo


@dataclass
class CommandContext:
    xdo: Xdo
    args: argparse.Namespace
    window_stack: T.List[int]


class BaseCommand:
    names: T.List[str] = NotImplemented
    description: str = NotImplemented

    @classmethod
    def run(cls, ctx: CommandContext) -> None:
        raise NotImplementedError("not implemented")

    @classmethod
    def decorate_arg_parser(cls, parser: argparse.ArgumentParser) -> None:
        pass
