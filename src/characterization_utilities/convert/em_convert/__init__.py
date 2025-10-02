import importlib
from typing import TYPE_CHECKING

from characterization_utilities.convert.em_convert.utils import base_matchers

if TYPE_CHECKING:
    from structlog.stdlib import BoundLogger


def load_matchers(tag_list: list, metadata: dict, logger: 'BoundLogger') -> list:
    """
    Carica dinamicamente il corretto array di matchers in base allo strumento
    da cui i dati provengono.
    """
    tag_finder = {50431: 'NISABA', 34682: 'HELIOS', 60000: 'VELION'}

    type_to_package = {
        'HELIOS': 'characterization_utilities.convert.em_convert.fei_helios_matcher',
        'NISABA': 'characterization_utilities.convert.em_convert.tescan_matcher',
        'VELION': 'characterization_utilities.convert.em_convert.raith_velion_matcher',
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
                    formatted or supported.
                    """
                )
            return flag

    flag = search_flag_for_matchers(tag_list, logger)

    if flag is None:
        logger.info(
            """
            Due to the absence of a good matcher routine, during the conversion 
            the base matchers were loaded.
            """
        )
        return base_matchers

    module_path = type_to_package[flag]
    module = importlib.import_module(module_path)
    logger.info(f'Matching routine loaded for {flag} from {module_path}')
    if hasattr(module, 'get_matchers'):
        logger.info(f'Loaded get_matchers for {flag} from {module_path}')
        return module.get_matchers(metadata)

    return getattr(module, 'matchers', None)
