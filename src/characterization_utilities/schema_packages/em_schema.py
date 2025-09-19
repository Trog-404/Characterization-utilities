from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

import os

from nomad.metainfo import MEnum, Package, Quantity, Section, SubSection
from pynxtools.definitions.dev_tools.utils.nxdl_utils import (
    get_app_defs_names,  # pylint: disable=import-error
)

from characterization_utilities.convert.em_convert.parser import write_data_to_nexus_new
from characterization_utilities.schema_packages.character import (
    Samplebase,
    SampleComponentbase,
)
from characterization_utilities.schema_packages.dataconverter import (
    CharacterizationStepConverter,
)

m_package = Package(name='Definitions to define an ELN for electron microscopy steps')


class SampleComponent(SampleComponentbase):
    m_def = Section(
        a_eln={
            'properties': {
                'order': [
                    'name',
                    'description',
                    'chemical_formula',
                    'datetime',
                    'component_id',
                    'datetime',
                ],
            },
        }
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)


class Sample(Samplebase):
    m_def = Section(
        a_eln={
            'properties': {
                'order': [
                    'name',
                    'description',
                    'chemical_formula',
                    'lab_id',
                    'datetime',
                    'id_wafer_parent',
                    'shapeType',
                    'is_simulation',
                    'type',
                    'physical_form',
                    'situation',
                    'atom_types',
                    'notes',
                ],
            },
        }
    )

    is_simulation = Quantity(type=bool, a_eln={'component': 'BoolEditQuantity'})
    physical_form = Quantity(
        type=MEnum('bulk', 'foil', 'powder', 'thin film'),
        a_eln={'component': 'EnumEditQuantity'},
    )
    atom_types = Quantity(type=str, a_eln={'component': 'StringEditQuantity'})

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)
        if self.chemical_formula:
            atoms = []
            for element_composition in self.elemental_composition:
                atoms.append(element_composition.element)
            self.atom_types = ', '.join(atoms)


class EmStepConverter(CharacterizationStepConverter):
    m_def = Section(
        a_eln={
            'hide': [
                'tag',
                'duration',
                'recipe_name',
                'recipe_file',
                'recipe_preview',
                'job_number',
                'keywords',
                'operator',
            ],
            'properties': {
                'order': [
                    'name',
                    'setp_id',
                    'description',
                    'affiliation',
                    'location',
                    'institution',
                    'facility',
                    'laboratory',
                    'id_item_processed',
                    'starting_date',
                    'ending_date',
                    'step_type',
                    'definition_of_process_step',
                    'nxdl',
                    'input_data_files',
                    'output',
                    'export',
                    'nexus_view',
                    'notes',
                ]
            },
        }
    )

    nxdl = Quantity(
        type=MEnum(sorted(list(set(get_app_defs_names())))),
        description='The nxdl needed for running the Nexus converter.',
        a_eln=dict(component='AutocompleteEditQuantity'),
        default='NXem',
    )

    samples = SubSection(section_def=Sample, repeats=True)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

        files_list = self.input_data_files
        raw_path = archive.m_context.raw_path()

        if self.output:
            output_file = os.path.join(raw_path, self.output)

        if files_list is not None and len(files_list) > 0 and self.nxdl:
            for file in files_list:
                to_write = os.path.join(raw_path, file)
                write_data_to_nexus_new(output_file, to_write, logger)


m_package.__init_metainfo__()
