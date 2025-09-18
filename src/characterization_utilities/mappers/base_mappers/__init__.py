from characterization_utilities.mappers.base_mappers.entry_mapper import (
    mapper as emapper,
)
from characterization_utilities.mappers.base_mappers.sample_mapper import (
    mapper as smapper,
)
from characterization_utilities.mappers.base_mappers.user_mapper import (
    mapper as umapper,
)

__all__ = ['emapper', 'umapper', 'smapper']

mapperMenager = {
    'Entry': {'mapper': emapper},
    'User': {'NX_class': 'NXuser', 'mapper': umapper},
    'Sample': {'NX_class': 'NXsample', 'mapper': smapper},
    'SampleComponent': {'NX_class': 'NXsample_component', 'mapper': smapper},
}
