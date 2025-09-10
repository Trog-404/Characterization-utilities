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

from nomad.datamodel.data import ArchiveSection
from nomad.metainfo import MEnum, Package, Quantity, Section, SubSection
from pynxtools.definitions.dev_tools.utils.nxdl_utils import (
    get_app_defs_names,  # pylint: disable=import-error
)
from schema_packages.fabrication_utilities import FabricationProcessStep
from schema_packages.Items import Sample

from characterization_nexus.schema_packages.convert.common import (
    instanciate_nexus,
    write_additional_from_list,
)
from characterization_nexus.schema_packages.convert.Tiff_to_dict_converter import (
    write_data_to_nexus,
)

m_package = Package(name='General instruments for characterization steps')


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

    additional_json_files_to_convert = Quantity(
        type=str,
        description='Here you can put all jsons for more details in the NeXus entry',
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

    sample = SubSection(section_def=Sample, repeats=False)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)
        raw_path = archive.m_context.raw_path()
        if self.export:
            list_to_convert = self.additional_json_files_to_convert
            if list_to_convert is not None and len(list_to_convert) > 0:
                instanciate_nexus(raw_path, self.output, self.nxdl)
                if len(self.input_data_files) > 0:
                    write_data_to_nexus(raw_path, self.input_data_files[0], self.output)
                write_additional_from_list(raw_path, list_to_convert, self.output)
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
