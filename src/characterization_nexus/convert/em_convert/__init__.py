import importlib


def load_matchers(flag: str) -> list:
    """
    Carica dinamicamente il corretto array di matchers in base allo strumento
    da cui i dati provengono.

    flag: stringa tipo 'FEI_HELIOS' o 'TESCAN'
    """
    type_to_package = {
        'FEI_HELIOS': 'characterization_nexus.convert.em_convert.fei_helios_matcher',
        'TESCAN': 'characterization_nexus.convert.em_convert.tescan_matcher',
        # aggiungi altri qui
    }

    if flag not in type_to_package:
        raise ValueError(f'File format from {flag} non supportato')

    module_path = type_to_package[flag]
    module = importlib.import_module(module_path)

    return getattr(module, 'matchers', None)
