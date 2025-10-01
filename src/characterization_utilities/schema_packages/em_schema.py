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

from characterization_utilities.convert.common import instanciate_nexus
from characterization_utilities.convert.em_convert.parser import write_data_to_nexus_new
from characterization_utilities.schema_packages.character import (
    CharacterizationStep,
    Samplebase,
    SampleComponentbase,
)
from characterization_utilities.schema_packages.dataconverter import (
    CharacterizationStepConverter,
)

m_package = Package(name='Classes to define an ELN for electron microscopy steps')


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

    components = SubSection(section_def=SampleComponent, repeats=True)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)
        if self.chemical_formula:
            atoms = []
            for element_composition in self.elemental_composition:
                atoms.append(element_composition.element)
            self.atom_types = ', '.join(atoms)


class EmStepConverter(CharacterizationStepConverter, CharacterizationStep):
    m_def = Section(
        description="""
        This is an instance of a NOMAD ELN suitable to manage electron microscopy 
        experiments. The idea is to allow the user to give information about the 
        measurement and the preliminary steps (according to CHADA taxonomy). In 
        addition the ELN allows to upload SEM measurement images that will be processed
        to extract all the possible metadata (if supported you will receive a complete
        output for which the use of a TIFF image format is recommended). You can also
        analyze your data preliminary thanks to the notebook at the git page
        https://www.github.com/Trog-404/Characterization-utilities.git. 
        """,
        a_eln={
            'hide': [
                'tag',
                'duration',
                'recipe_name',
                'recipe_file',
                'recipe_preview',
                'keywords',
            ],
            'properties': {
                'order': [
                    'name',
                    'step_id',
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
        },
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
            if self.nxdl:
                list_dict = archive.data.__dict__
                instanciate_nexus(output_file, list_dict, self.nxdl, logger)
                if files_list is not None and len(files_list) > 0:
                    for file in files_list:
                        to_write = os.path.join(raw_path, file)
                        write_data_to_nexus_new(output_file, to_write, logger)
                try:
                    archive.m_context.process_updated_raw_file(
                        self.output, allow_modify=True
                    )
                except Exception as e:
                    logger.error(
                        'could not trigger processing', mainfile=self.output, exc_info=e
                    )
                else:
                    logger.info('triggered processing', mainfile=self.output)
                self.nexus_view = f'../upload/archive/mainfile/{self.output}#/data'


m_package.__init_metainfo__()
