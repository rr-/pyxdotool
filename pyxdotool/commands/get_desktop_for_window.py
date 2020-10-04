import argparse

from pyxdotool.commands.base import BaseCommand, CommandContext


class GetDesktopForWindowCommand(BaseCommand):
    names = ["get_desktop_for_window"]
    description = (
        "Output the desktop currently containing the given window. Move a "
        "window to a different desktop. If no window is given, %%1 is the "
        'default. See WINDOW STACK and "COMMAND CHAINING" for more details.'
    )

    @classmethod
    def decorate_arg_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "window_id",
            type=int,
            help="window id to get desktop for",
            nargs="?",
        )

    @classmethod
    def run(cls, ctx: CommandContext) -> None:
        try:
            window_id = ctx.args.window_id or ctx.window_stack.pop()
        except IndexError:
            raise IndexError("Must specify window")

        print(ctx.xdo.get_desktop_for_window(window_id))
