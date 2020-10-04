import argparse

from pyxdotool.commands.base import BaseCommand, CommandContext


class GetWindowFocusCommand(BaseCommand):
    names = ["getwindowfocus"]
    description = (
        "Prints the window id of the currently focused window. Saves the "
        'result to the window stack. See "WINDOW STACK" for more details.\n'
        "\n"
        "If the current window has no WM_CLASS property, we assume it is not "
        "a normal top-level window and traverse up the parents until we find "
        "a window with a WM_CLASS set and return that window id.\n"
        "\n"
        "If you really want the window currently having focus and don't care "
        "if it has a WM_CLASS setting, then use 'getwindowfocus -f'."
    )

    @classmethod
    def decorate_arg_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-f",
            dest="get_toplevel_focus",
            action="store_false",
            help=(
                "Report the window with focus even if we don't think it is a "
                "top-level window. The default is to find the top-level "
                "window that has focus."
            ),
        )

    @classmethod
    def run(cls, ctx: CommandContext) -> None:
        ctx.window_stack.append(
            ctx.xdo.get_focused_window_sane()
            if ctx.args.get_toplevel_focus
            else ctx.xdo.get_focused_window()
        )
