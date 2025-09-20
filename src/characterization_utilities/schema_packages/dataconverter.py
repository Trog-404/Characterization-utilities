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
from nomad.metainfo import MEnum, Package, Quantity, Section
from pynxtools.definitions.dev_tools.utils.nxdl_utils import (
    get_app_defs_names,  # pylint: disable=import-error
)

m_package = Package(name='General class to convert characterization steps to NeXus')


class CharacterizationStepConverter(ArchiveSection):
    m_def = Section(
        description="""Ideal class to inherit to allow transformation of proprietary
        formats in the NeXus standard for characterization steps.
        """,
        a_eln={
            'properties': {
                'order': [
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

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        raw_path = archive.m_context.raw_path()
        if self.export:
            output_file = os.path.join(raw_path, self.output)
            try:
                os.remove(output_file)
                archive.m_context.process_updated_raw_file(
                    archive.data.output, allow_modify=True
                )
            except Exception:
                pass
        super().normalize(archive, logger)


m_package.__init_metainfo__()
