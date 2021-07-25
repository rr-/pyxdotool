import argparse

from pyxdotool.commands.base import BaseCommand, CommandContext


class GetWindowPidCommand(BaseCommand):
    names = ["getwindowpid"]
    description = (
        "Output the PID owning a given window. This requires effort from the "
        "application owning a window and may not work for all windows. This "
        'uses _NET_WM_PID property of the window. See "EXTENDED WINDOW '
        'MANAGER HINTS" below for more information.\n'
        "\n"
        "If no window is given, the default is %%1. If no windows are on "
        'the stack, then this is an error. See "WINDOW STACK" for more details.'
    )

    @classmethod
    def decorate_arg_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "window_id",
            type=int,
            help="window id to get the PID of",
            nargs="?",
        )

    @classmethod
    def run(cls, ctx: CommandContext) -> None:
        try:
            window_id = ctx.args.window_id or ctx.window_stack.pop()
        except IndexError as ex:
            raise IndexError("Must specify window") from ex

        print(ctx.xdo.get_window_pid(window_id))
