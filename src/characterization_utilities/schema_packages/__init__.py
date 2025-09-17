from nomad.config.models.plugins import SchemaPackageEntryPoint


class EmSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from characterization_utilities.schema_packages.em_schema import m_package

        return m_package


em_schema_package_entry_point = EmSchemaPackageEntryPoint(
    name='EmSchemaPackage',
    description='New schema package entry point for electron microscopy to nexus.',
)

#class CharacterizationEntryPoint(SchemaPackageEntryPoint):
#    def load(self):
#        from schema_packages.steps.character import m_package
#
#        return m_package
#
#
#Characterization_entry_point = CharacterizationEntryPoint(
#    name='Characterization steps',
#    description='Schema package for describing charac steps in fabrications.',
#)
#
#
#class CharacterizationEquipmentEntryPoint(SchemaPackageEntryPoint):
#    def load(self):
#        from schema_packages.equipments.character_equipment import (
#            m_package,
#        )
#
#        return m_package
#
#
#Characterization_Equipment_entry_point = CharacterizationEquipmentEntryPoint(
#    name='Characterization tools',
#    description="""
#        Schema package to describe characterization tools used in fabrications to
#         control process steps.'
#    """,
#)