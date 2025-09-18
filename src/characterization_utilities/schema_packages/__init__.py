from nomad.config.models.plugins import SchemaPackageEntryPoint


class CharacterizationEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from characterization_utilities.schema_packages.character import m_package

        return m_package


Characterization_entry_point = CharacterizationEntryPoint(
    name='Characterization steps',
    description='Schemas to describe general characterization steps.',
)


class DataConverterEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from characterization_utilities.schema_packages.dataconverter import m_package

        return m_package


Dataconverter_entry_point = DataConverterEntryPoint(
    name='Characterization steps',
    description='Schemas to allow NeXus conversion for characterization steps.',
)


class EmSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from characterization_utilities.schema_packages.em_schema import m_package

        return m_package


Em_schema_package_entry_point = EmSchemaPackageEntryPoint(
    name='EmSchemaPackage',
    description='Schemas entry point for electron microscopy to nexus.',
)

# class CharacterizationEquipmentEntryPoint(SchemaPackageEntryPoint):
#    def load(self):
#        from schema_packages.equipments.character_equipment import (
#            m_package,
#        )
#
#        return m_package
#
#
# Characterization_Equipment_entry_point = CharacterizationEquipmentEntryPoint(
#    name='Characterization tools',
#    description="""
#        Schema package to describe characterization tools used in fabrications to
#         control process steps.'
#    """,
# )
