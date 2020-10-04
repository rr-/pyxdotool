import argparse
import sys
import typing as T

from pyxdotool.commands.base import BaseCommand, CommandContext
from pyxdotool.xdo import Xdo


def parse_args(
    argv: T.Optional[T.List[str]] = None,
) -> T.Iterable[argparse.Namespace]:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    for command_cls in BaseCommand.__subclasses__():
        subparser = subparsers.add_parser(
            command_cls.names[0],
            aliases=command_cls.names[1:],
            description=(
                None
                if command_cls.description is NotImplemented
                else command_cls.description
            ),
        )
        subparser.set_defaults(command_cls=command_cls)
        command_cls.decorate_arg_parser(subparser)

    rest = argv
    while rest:
        restprev = rest[:]
        args, rest = parser.parse_known_args(rest)
        yield args
        if rest == restprev:
            parser.error(f"unrecognized arguments: {rest[0]}")
            break


def main() -> None:
    args_list = list(parse_args(sys.argv[1:]))

    window_stack: T.List[int] = []
    xdo = Xdo()

    for args in args_list:
        ctx = CommandContext(xdo, args, window_stack)
        command = args.command_cls()
        command.run(ctx)

    for window_id in window_stack:
        print(window_id)


if __name__ == "__main__":
    main()
