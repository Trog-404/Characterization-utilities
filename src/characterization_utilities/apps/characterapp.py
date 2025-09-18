# from apps.characterization.directories import dir_path
# from nomad.config.models.ui import (
#    App,
#    Column,
#    Menu,
#    MenuItemCustomQuantities,
#    SearchQuantities,
# )
#
# schemas = [
#    f'*#{path_value}'
#    for path_value in dir_path.values()
#    if 'steps.character' in path_value
# ]
#
# fps = 'FabricationProcessStep'
# dir0 = f'schema_packages.fabrication_utilities.{fps}'
# schemas.append(f'*#{dir0}')
#
# characterapp = App(
#    label='Characterization steps',
#    path='carachterapp',
#    category='Characterization utilities',
#    description='App to search characterization steps.',
#    readme="""
#    This app is intended to navigate around the ecosystem of clean room fabrication
#    possible characterization steps. At the beginning you will see all the fabrication
#    steps available in nomad and than through the filters on the left you can
#    specialize the research per single technique. Navigation across multiple technique
#    is not allowed. Moreover this app is intended as a temporary support for this kind
#    of steps because in the future we hope to built NeXus schemas for all
#    characterization. For this reason the steps supported by the pynxtools can be
#    reached via other apps.
#    """,
#    search_quantities=SearchQuantities(include=schemas),
#    columns=[
#        Column(quantity='entry_name', selected=True),
#        Column(quantity='entry_type', selected=True),
#        Column(
#            quantity=f'data.affiliation#{dir0}',
#            selected=True,
#        ),
#        Column(
#            quantity=f'data.location#{dir0}',
#            selected=True,
#        ),
#        Column(quantity='upload_create_time', selected=True),
#        Column(quantity=f'data.recipe_name#{dir0}'),
#    ],
#    filters_locked={'section_defs.definition_qualified_name': dir0},
#    menu=Menu(
#        items=[
#            Menu(
#                title='1st main category',
#            ),
#            Menu(
#                title='User defined quantities',
#                items=[
#                    MenuItemCustomQuantities(
#                        title='Costumer user quantities',
#                        type='custom_quantities',
#                    ),
#                ],
#            ),
#        ],
#    ),
# )
#
