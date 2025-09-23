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

# Sample is a particular instance of the Item used in the fabrication workflow.
# Item is in general a component upon which series of transformation or
# characteriaztion, in general operation, are performed. Sample is specifically the
# component which after the preparation activity enter in the characterization
# experiment.

m_package = Package(name='Base schema to describe characetrization steps.')


class History(Activity):
    m_def = Section()

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        pass

    ## Inseriata così solo per sopprimere la normalizzazione della classe padre
    # che risulta avere bugs.


class SampleComponentbase(ItemComponent):
    m_def = Section(
        description="""
        Class to inherit to define descriptor of sample components and their history
        """,
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
        },
    )

    history = SubSection(
        section_def=History,
        description='Here you can briefly describe the preparation of the component',
        repeats=False,
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)


class Samplebase(Item):
    m_def = Section(
        description="""
        Ideal class to inherit and which must be specilized in useful
        instances to describe real sample descriptor class for each characterization
        techique. Following the CHADA instructions sample is always described with a
        description of the activities used to prepare it.
        """,
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
        },
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
        section_def=History,
        description='Here you can briefly describe the preparation of the item',
        repeats=False,
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)


class CharacterizationStep(FabricationProcessStep):
    m_def = Section(
        description="""
        This is an instance of a NOMAD ELN suitable to manage electron microscopy 
        experiments. The idea is to allow the user to give information about the 
        measurement and the preliminary steps (according to CHADA taxonomy).
        """,
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
        },
    )

    samples = SubSection(section_def=Samplebase, repeats=True)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)


m_package.__init_metainfo__()
