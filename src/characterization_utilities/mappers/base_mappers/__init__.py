from characterization_utilities.mappers.base_mappers.entry_mapper import (
    mapper as emapper,
)
from characterization_utilities.mappers.base_mappers.sample_mapper import (
    comp_mapper as cmapper,
)
from characterization_utilities.mappers.base_mappers.sample_mapper import (
    sample_mapper as smapper,
)
from characterization_utilities.mappers.base_mappers.user_mapper import (
    mapper as umapper,
)

__all__ = ['emapper', 'umapper', 'smapper', 'cmapper']

mapperMenager = {
    'Entry': {'mapper': emapper},
    'User': {'NX_class': 'NXuser', 'mapper': umapper},
    'Samplebase': {'NX_class': 'NXsample', 'mapper': smapper},
    'SampleComponentbase': {'NX_class': 'NXsample_component', 'mapper': cmapper},
    'History': {'NX_class': 'NXhistory', 'mapper': {'identifierNAME': 'lab_id'}},
    'ActivityStep': {
        'NX_class': 'NXactivity',
        'mapper': {'description': ' description', 'start_time': 'start_time'},
    },
}
