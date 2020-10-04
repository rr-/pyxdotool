import argparse
import time

from pyxdotool.commands.base import BaseCommand, CommandContext


class SleepCommand(BaseCommand):
    names = ["sleep"]
    description = (
        "Sleep for a specified period. Fractions of seconds (like 1.3, or "
        "0.4) are valid, here."
    )

    @classmethod
    def decorate_arg_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("seconds", type=float, help="number of seconds")

    @classmethod
    def run(cls, ctx: CommandContext) -> None:
        time.sleep(ctx.args.seconds)
