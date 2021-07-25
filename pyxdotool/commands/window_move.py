import argparse
import re

from pyxdotool.commands.base import BaseCommand, CommandContext


class WindowMoveCommand(BaseCommand):
    names = ["windowmove"]
    description = """Move the window.

If the given x coordinate is literally 'x', then the window's current x position will be unchanged. The same applies for 'y'. Percentages are valid for width and height. They are relative to the geometry of the screen the window is on.

If no window is given, %%1 is the default. See "WINDOW STACK" and "COMMAND CHAINING" for more details.
"""

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
        parser.add_argument(
            "--relative",
            action="store_true",
            help="make movements relative to the current window position",
        )
        parser.add_argument("x")
        parser.add_argument("y")

    @classmethod
    def run(cls, ctx: CommandContext) -> None:
        try:
            window_id = ctx.args.window_id or ctx.window_stack.pop()
        except IndexError as ex:
            raise IndexError("Must specify window") from ex

        orig_x, orig_y, screen_id = ctx.xdo.get_window_location(window_id)

        if screen_id is None:
            raise RuntimeError("window has no screen")
        screen_w, screen_h = ctx.xdo.get_screen_size(screen_id)

        target_x = cls.resolve_coord(
            ctx.args.x, orig_x, screen_w, "x", is_relative=ctx.args.relative
        )
        target_y = cls.resolve_coord(
            ctx.args.y, orig_y, screen_h, "y", is_relative=ctx.args.relative
        )

        ctx.xdo.move_window(window_id, target_x, target_y)

        if ctx.args.sync and (target_x != orig_x or target_y != orig_y):
            # Permit imprecision to account for window borders and titlebar
            new_x = float("Inf")
            new_y = float("Inf")
            while (
                orig_x == new_x
                and orig_y == new_y
                and abs(target_x - new_x) > 10
                and abs(target_y - new_y) > 50
            ):
                new_x, new_y, screen_id = ctx.xdo.get_window_location(
                    window_id
                )

    @staticmethod
    def resolve_coord(
        user_input: str,
        orig_coord: int,
        screen_size: int,
        neutral_coord: str,
        is_relative: bool,
    ) -> int:
        if user_input == neutral_coord:
            return orig_coord

        if match := re.match(r"(\d+(\.\d+)?)%", user_input):
            target_coord = int(screen_size * float(match.group(1)) / 100)
        elif match := re.match(r"(\d+)", user_input):
            target_coord = int(match.group(1))
        else:
            raise ValueError(f"unknown coord: {user_input}")

        if is_relative:
            return orig_coord + target_coord
        return target_coord
