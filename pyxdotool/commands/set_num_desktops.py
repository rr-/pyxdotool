import argparse

from pyxdotool.commands.base import BaseCommand, CommandContext


class SetNumberOfDesktopsCommand(BaseCommand):
    names = ["set_num_desktops"]
    description = "Changes the number of desktops or workspaces."

    @classmethod
    def decorate_arg_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "num_desktops", type=int, help="new number of desktops"
        )

    @classmethod
    def run(cls, ctx: CommandContext) -> None:
        ctx.xdo.set_number_of_desktops(ctx.args.num_desktops)
