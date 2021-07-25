import argparse

from pyxdotool.commands.base import BaseCommand, CommandContext


class SetScreenForWindowCommand(BaseCommand):
    names = ["set_screen_for_window"]
    description = (
        "Move a window to a different screen. If no window is given, %%1 is "
        'the default. See "WINDOW STACK" and "COMMAND CHAINING" for more '
        "details."
    )

    @classmethod
    def decorate_arg_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "window_id",
            type=int,
            help="window id to set screen for",
            nargs="?",
        )
        parser.add_argument("screen", type=int, help="screen to set")
        parser.add_argument(
            "--relative",
            action="store_true",
            help=(
                "use relative movements instead of absolute. This lets you "
                "move relative to the current screen."
            ),
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

        screens = ctx.xdo.query_screens()

        for window_id in window_ids:
            win_w, win_h = ctx.xdo.get_window_size(window_id)
            win_x, win_y, screen_id = ctx.xdo.get_window_location(window_id)

            source_screen = screens[screen_id]
            if ctx.args.relative:
                target_screen = screens[
                    (screen_id + ctx.args.screen) % len(screens)
                ]
            else:
                try:
                    target_screen = screens[ctx.args.screen]
                except IndexError:
                    raise IndexError(f"Invalid screen {screen_id}") from ex

            if source_screen == target_screen:
                continue

            target_x = int(
                target_screen.x
                + target_screen.width
                * (win_x + win_w / 2 - source_screen.x)
                / source_screen.width
                - win_w / 2
            )
            target_y = int(
                target_screen.y
                + target_screen.height
                * (win_y + win_h / 2 - source_screen.y)
                / source_screen.height
                - win_h / 2
            )
            ctx.xdo.move_window(window_id, target_x, target_y)
