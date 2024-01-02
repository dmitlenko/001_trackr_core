from trackr.cli import cli_main


if __name__ == '__main__':
    # cli_main()

    from trackr.core.module import SearchModule
    from pprint import pprint
    module = SearchModule.from_yaml("modules/metro.yaml")
    result = module.search("вода", "00018")[:3]
    pprint(result)

