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

from nomad.datamodel.data import ArchiveSection, EntryData

from nomad.metainfo import (
    MEnum,
    Package,
    Quantity,
    Section,
)

from pynxtools.definitions.dev_tools.utils.nxdl_utils import (
    get_app_defs_names,  # pylint: disable=import-error
)

from schema_packages.fabrication_utilities import FabricationProcessStep


m_package = Package(name='General instruments for characterization steps')


class BaseConverter(ArchiveSection, EntryData):

    m_def=Section()

    nxdl = Quantity(
        type=MEnum(sorted(list(set(get_app_defs_names())))),
        description="The nxdl needed for running the Nexus converter.",
        a_eln=dict(component="AutocompleteEditQuantity"),
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)


m_package.__init_metainfo__()
