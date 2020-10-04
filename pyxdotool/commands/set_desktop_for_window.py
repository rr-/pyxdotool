import argparse

from pyxdotool.commands.base import BaseCommand, CommandContext


class SetDesktopForWindowCommand(BaseCommand):
    names = ["set_desktop_for_window"]
    description = (
        "Move a window to a different desktop. If no window is given, %%1 is "
        'the default. See "WINDOW STACK" and "COMMAND CHAINING" for more '
        "details."
    )

    @classmethod
    def decorate_arg_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "window_id",
            type=int,
            help="window id to set desktop for",
            nargs="?",
        )
        parser.add_argument("desktop", type=int, help="desktop to set")

    @classmethod
    def run(cls, ctx: CommandContext) -> None:
        if ctx.args.window_id:
            window_ids = [ctx.args.window_id]
        elif ctx.window_stack:
            window_ids = ctx.window_stack[:]
            ctx.window_stack[:] = []
        else:
            raise IndexError("Must specify window")

        for window_id in window_ids:
            ctx.xdo.set_desktop_for_window(window_id, ctx.args.desktop)
