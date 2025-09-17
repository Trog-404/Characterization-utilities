from characterization_utilities.mappers.base_mappers import smapper

smapper.update(
    {
        'is_simulation': 'is_simulation',
        'atom_types': 'atom_types',
        'id_wafer_parent': 'identifier_parent',
        'lab_id': 'identifier_sample',
    }
)

mapper = smapper
