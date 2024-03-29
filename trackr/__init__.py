import logging


VERSION = (1, 0, 0)
LOGGING_FORMAT = '%(asctime)s :: %(name)-36s :: %(levelname)-8s :: %(message)s'
MODULE_FILE_EXTENSION = '.ysm'


__version__ = '.'.join(map(str, VERSION))


logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO)
