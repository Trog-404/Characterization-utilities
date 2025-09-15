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

from nomad.datamodel.data import ArchiveSection
from nomad.datamodel.metainfo.basesections.v2 import Activity
from nomad.metainfo import MEnum, Package, Quantity, Section, SubSection
from pynxtools.definitions.dev_tools.utils.nxdl_utils import (
    get_app_defs_names,  # pylint: disable=import-error
)
from schema_packages.fabrication_utilities import FabricationProcessStep
from schema_packages.Items import Item, ItemComponent

from characterization_nexus.convert.common import instanciate_nexus
from characterization_nexus.convert.em_convert.parser import write_data_to_nexus

m_package = Package(name='General instruments for characterization steps')

class SampleComponentbase(ItemComponent):
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

    history = SubSection(
        section_def=Activity,
        description='Here you can briefly describe the preparation of the component',
        repeats=False,
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)


class Samplebase(Item):
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
                    'type',
                    'physical_form',
                    'situation',
                    'notes',
                ],
            },
        }
    )
    type = Quantity(
        type=MEnum(
            'sample',
            'sample+can',
            'can',
            'sample+buffer',
            'buffer',
            'calibration sample',
            'normalization sample',
            'simulated data',
            'none',
            'sample environment',
        ),
        a_eln={'component': 'EnumEditQuantity'},
    )

    physical_form = Quantity(
        type=MEnum(
            'crystal',
            'foil',
            'pellet',
            'powder',
            'thin film',
            'disc',
            'foam',
            'gas',
            'liquid',
            'amorphous',
        ),
        a_eln={'component': 'EnumEditQuantity'},
    )

    situation = Quantity(
        type=MEnum(
            'air',
            'vacuum',
            'inert atmosphere',
            'oxidising atmosphere',
            'reducing atmosphere',
            'sealed can',
            'other',
        ),
        a_eln={'component': 'EnumEditQuantity'},
    )
    components = SubSection(
        section_def=SampleComponentbase,
        description='If the sample has different compoents you can describe them here',
        repeats=True,
    )
    history = SubSection(
        section_def=Activity,
        description='Here you can briefly describe the preparation of the item',
        repeats=False,
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)


class CharacterizationStepConverter(FabricationProcessStep):
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
                    'additional_data_to_convert',
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
    )

    input_data_files = Quantity(
        type=str,
        description='Here you can put all data files to convert to NeXus',
        shape=['*'],
        a_eln={'component': 'FileEditQuantity'},
    )

    output = Quantity(
        type=str,
        description='Output Nexus filename to save all the data. Default: output.nxs',
        a_eln=dict(component='StringEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
        default='output.nxs',
    )

    export = Quantity(
        type=bool,
        description='If true conversion shall happen automatically when ELN is saved',
        a_eln=dict(component='BoolEditQuantity'),
        default=True,
    )

    nexus_view = Quantity(
        type=ArchiveSection,
        description='Link to the NeXus Entry',
        a_eln=dict(overview=True),
    )

    samples = SubSection(section_def=Samplebase, repeats=True)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        raw_path = archive.m_context.raw_path()
        files_list = self.input_data_files
        if self.export:
            output_file = os.path.join(raw_path, self.output)
            try:
                os.remove(output_file)
                archive.m_context.process_updated_raw_file(
                    archive.data.output, allow_modify=True
                )
            except Exception:
                pass
            if self.nxdl:
                instanciate_nexus(output_file, archive.data, self.nxdl)
                if files_list is not None and len(files_list) > 0:
                    for file in files_list:
                        to_write = os.path.join(raw_path, file)
                        write_data_to_nexus(output_file, to_write)
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
        super().normalize(archive, logger)


m_package.__init_metainfo__()
