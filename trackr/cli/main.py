import argparse, logging


from trackr import __version__, LOGGING_FORMAT


logger = logging.getLogger(__name__)


def compile_argument_group():
    group = argparse.ArgumentParser(add_help=False)

    group.add_argument("module", type=str, help="path to search module")
    group.add_argument("-o", "--output", type=str, help="path to output file")

    return group


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v", "--version", action="version", version=f"trackr-cli {__version__}"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="enable debug output"
    )
    parser.add_argument("-l", "--log", type=str, help="path to log file")
    parser.add_argument("-q", "--quiet", action="store_true", help="disable output")

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "compile", parents=[compile_argument_group()], help="compile a search module"
    )

    return parser.parse_args()


def compile(args):
    from trackr.cli.compiler import compile_module

    compile_module(args.module, args.output)


def cli_main():
    args = parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug output enabled")

    if args.log:
        handler = logging.FileHandler(args.log)
        handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        logging.getLogger().addHandler(handler)

    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)

    if args.command == "compile":
        compile(args)
