from trackr.cli import cli_main


def avg(d: list):
    return sum(d) / len(d)


if __name__ == '__main__':
    cli_main()
