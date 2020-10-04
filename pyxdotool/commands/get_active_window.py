from pyxdotool.commands.base import BaseCommand, CommandContext


class GetActiveWindowCommand(BaseCommand):
    names = ["getactivewindow"]
    description = (
        "Output the current active window. This command is often more "
        "reliable than getwindowfocus. The result is saved to the window "
        'stack. See "WINDOW STACK" for more details.'
    )

    @classmethod
    def run(cls, ctx: CommandContext) -> None:
        ctx.window_stack.append(ctx.xdo.get_active_window())
