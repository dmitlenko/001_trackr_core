import logging, pickle

from trackr.core.module import SearchModule


logger = logging.getLogger(__name__)


def compile_module(file_path: str,  output_path: str = None) -> None:
    logger.info(f'Compiling search module: {file_path}')
    logger.debug(f' {output_path=}')

    try:
        module = SearchModule.from_yaml(file_path, is_compilation=True)
    except Exception as e:
        logger.error(f'Failed to compile module: {file_path}')
        logger.exception(e)
        return

    if output_path is None:
        output_path = f'{file_path.split(".", 1)[0]}.compiledmodule'

        logger.info(f'No output path was specified, using default: {output_path}')

    with open(output_path, 'wb') as file:
        pickle.dump(module, file)
