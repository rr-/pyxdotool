import argparse

from pyxdotool.commands.base import BaseCommand, CommandContext


class GetWindowGeometryCommand(BaseCommand):
    names = ["getwindowgeometry"]
    description = """Output the geometry (location and position) of a window. The values
        include: x, y, width, height, and screen number.
        """

    @classmethod
    def decorate_arg_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "window_id",
            type=int,
            help="window id to set desktop for",
            nargs="?",
        )
        parser.add_argument(
            "-s",
            "--shell",
            dest="shell_output",
            help="Output values suitable for 'eval' in a shell.",
            action="store_true",
        )
        parser.add_argument(
            "-p",
            "--prefix",
            help="use prefix for shell variables names",
            default="",
        )

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
            win_w, win_h = ctx.xdo.get_window_size(window_id)
            win_x, win_y, screen_id = ctx.xdo.get_window_location(window_id)
            if ctx.args.shell_output:
                print(f"{ctx.args.prefix}WINDOW={window_id}")
                print(f"{ctx.args.prefix}X={win_x}")
                print(f"{ctx.args.prefix}Y={win_y}")
                print(f"{ctx.args.prefix}WIDTH={win_w}")
                print(f"{ctx.args.prefix}HEIGHT={win_h}")
                print(f"{ctx.args.prefix}SCREEN={screen_id}")
            else:
                print(f"Window {window_id}")
                print(f"  Position: {win_x},{win_y} (screen: {screen_id})")
                print(f"  Geometry: {win_w}x{win_h}")
