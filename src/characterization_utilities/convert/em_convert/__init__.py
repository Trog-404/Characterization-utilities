import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from structlog.stdlib import BoundLogger


def load_matchers(tag_list: list, logger: 'BoundLogger') -> list:
    """
    Carica dinamicamente il corretto array di matchers in base allo strumento
    da cui i dati provengono.
    """
    tag_finder = {50431: 'NISABA', 34682: 'HELIOS'}

    type_to_package = {
        'HELIOS': 'characterization_utilities.convert.em_convert.fei_helios_matcher',
        'NISABA': 'characterization_utilities.convert.em_convert.tescan_matcher',
        # aggiungi altri qui
    }

    def search_flag_for_matchers(tag_list: list, logger) -> str | None:
        flag = None
        if tag_list is not None and len(tag_list) > 0:
            for tag in tag_list:
                if tag.code in tag_finder:
                    flag = tag_finder[tag.code]
            if flag is None:
                logger.warning(
                    """
                    No tags match in the registry. Probably file not correctly
                    formatted or supported. During the conversion the base
                    matchers are loaded
                    """
                )
            return flag

    flag = search_flag_for_matchers(tag_list, logger)

    if flag is None:
        logger.warning('File format non supportato')
        raise ValueError(f'File format from {flag} non supportato')

    module_path = type_to_package[flag]
    module = importlib.import_module(module_path)

    return getattr(module, 'matchers', None)
