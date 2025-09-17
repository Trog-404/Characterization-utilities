import importlib


def load_mapper_manager(output_type: str):
    """
    Carica dinamicamente il dizionario mapperMenager
    dal pacchetto corretto (es. em_mappers, afm_mappers, ...).

    output_type: stringa tipo 'NXem' o 'NXafm'
    """
    # mappatura tra output_type e package
    type_to_package = {
        'NXem': 'characterization_utilities.mappers.em_mappers',
        'NXafm': 'characterization_utilities.mappers.afm_mappers',
        # aggiungi altri qui
    }

    if output_type not in type_to_package:
        raise ValueError(f'Output type {output_type} non supportato')

    module_path = type_to_package[output_type]
    module = importlib.import_module(module_path)

    return getattr(module, 'mapperMenager', None)
