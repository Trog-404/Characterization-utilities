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

from nomad.datamodel.metainfo.basesections.v2 import Activity
from nomad.metainfo import MEnum, Package, Quantity, Section, SubSection
from schema_packages.fabrication_utilities import FabricationProcessStep
from schema_packages.Items import Item, ItemComponent

m_package = Package(name='Base schema to describe characetrization steps.')


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


class CharacterizationStep(FabricationProcessStep):
    m_def = Section(
        a_eln={
            'hide': [
                'tag',
                'duration',
            ],
            'properties': {
                'order': [
                    'name',
                    'description',
                    'affiliation',
                    'location',
                    'institution',
                    'facility',
                    'laboratory',
                    'keywords',
                    'id_item_processed',
                    'starting_date',
                    'ending_date',
                    'step_type',
                    'step_id',
                    'definition_of_process_step',
                    'recipe_name',
                    'recipe_file',
                    'recipe_preview',
                    'notes',
                ]
            },
        }
    )

    samples = SubSection(section_def=Samplebase, repeats=True)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)


m_package.__init_metainfo__()
