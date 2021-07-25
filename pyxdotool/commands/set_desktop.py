import argparse

from pyxdotool.commands.base import BaseCommand, CommandContext


class SetDesktopCommand(BaseCommand):
    names = ["set_desktop"]
    description = "Change the current view to the specified desktop."

    @classmethod
    def decorate_arg_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("desktop", type=int, help="desktop to switch to")
        parser.add_argument(
            "--relative",
            action="store_true",
            help=(
                "use relative movements instead of absolute. This lets you "
                "move relative to the current desktop."
            ),
        )

    @classmethod
    def run(cls, ctx: CommandContext) -> None:
        target_desktop = ctx.args.desktop
        if ctx.args.relative:
            target_desktop += ctx.xdo.get_current_desktop()
        ctx.xdo.set_current_desktop(target_desktop)
