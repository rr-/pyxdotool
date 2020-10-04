import argparse

from pyxdotool.commands.base import BaseCommand, CommandContext


class WindowActivateCommand(BaseCommand):
    names = ["windowactivate"]
    description = (
        "Activate the window. This command is different from windowfocus: "
        "if the window is on another desktop, we will switch to that desktop. "
        "It also uses a different method for bringing the window up. "
        "I recommend trying this command before using windowfocus, as it will "
        "work on more window managers.\n"
        "\n"
        'If no window is given, %%1 is the default. See "WINDOW STACK" and '
        '"COMMAND CHAINING" for more details.'
    )

    @classmethod
    def decorate_arg_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--sync",
            action="store_true",
            help=(
                "After sending the window activation, wait until the window "
                "is actually activated. This is useful for scripts that "
                "depend on actions being completed before moving on."
            ),
        )
        parser.add_argument(
            "window_id", type=int, help="window id to activate", nargs="?"
        )

    @classmethod
    def run(cls, ctx: CommandContext) -> None:
        try:
            window_id = ctx.args.window_id or ctx.window_stack.pop()
        except IndexError:
            raise IndexError("Must specify window")

        ctx.xdo.activate_window(window_id)
        if ctx.args.sync:
            ctx.xdo.wait_for_window_active(window_id, active=True)
