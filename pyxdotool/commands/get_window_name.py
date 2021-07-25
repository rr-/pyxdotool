import argparse

from pyxdotool.commands.base import BaseCommand, CommandContext


class GetWindowNameCommand(BaseCommand):
    names = ["getwindowname"]
    description = (
        "Output the name of a given window, also known as the title. This is "
        "the text displayed in the window's titlebar by your window manager.\n"
        "\n"
        "If no window is given, the default is %%1. If no windows are on "
        'the stack, then this is an error. See "WINDOW STACK" for more details.'
    )

    @classmethod
    def decorate_arg_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "window_id",
            type=int,
            help="window id to get the name of",
            nargs="?",
        )

    @classmethod
    def run(cls, ctx: CommandContext) -> None:
        try:
            window_id = ctx.args.window_id or ctx.window_stack.pop()
        except IndexError as ex:
            raise IndexError("Must specify window") from ex

        print(ctx.xdo.get_window_name(window_id))
