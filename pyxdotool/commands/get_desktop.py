from pyxdotool.commands.base import BaseCommand, CommandContext


class GetDesktopCommand(BaseCommand):
    names = ["get_desktop"]
    description = "Output the current desktop in view."

    @classmethod
    def run(cls, ctx: CommandContext) -> None:
        print(ctx.xdo.get_current_desktop())
