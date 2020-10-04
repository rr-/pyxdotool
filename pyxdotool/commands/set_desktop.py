import argparse

from pyxdotool.commands.base import BaseCommand, CommandContext


class SetDesktopCommand(BaseCommand):
    names = ["set_desktop"]
    description = "Change the current view to the specified desktop."

    @classmethod
    def decorate_arg_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("desktop", type=int, help="desktop to switch to")

    @classmethod
    def run(cls, ctx: CommandContext) -> None:
        ctx.xdo.set_current_desktop(ctx.args.desktop)
