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
from nomad.metainfo import MEnum, Package, Quantity, Section, SubSection
from pynxtools.definitions.dev_tools.utils.nxdl_utils import (
    get_app_defs_names,  # pylint: disable=import-error
)
from schema_packages.fabrication_utilities import FabricationProcessStep
from schema_packages.Items import Sample

from characterization_nexus.convert.common import (
    instanciate_nexus,
    write_sub_from_nomad,
)
from characterization_nexus.mappers import sample_mapper as smap
from characterization_nexus.mappers import user_mapper as umap

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
                instanciate_nexus(output_file, archive.data)
                if files_list is not None and len(files_list) > 0:
                    pass
                if self.users is not None and len(self.users) > 0:
                    users = list(archive.data.users)
                    for user in users:
                        write_sub_from_nomad(output_file, user, umap)
                if self.sample:
                    sample = archive.data.sample
                    for el in sample:
                        logger.info(f'Elemento dentro Sample è {el}')
                    write_sub_from_nomad(output_file, sample, smap)
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
