from pyxdotool.commands.base import BaseCommand, CommandContext


class GetNumberOfDesktopsCommand(BaseCommand):
    names = ["get_num_desktops"]
    description = "Output the current number of desktops."

    @classmethod
    def run(cls, ctx: CommandContext) -> None:
        print(ctx.xdo.get_number_of_desktops())
