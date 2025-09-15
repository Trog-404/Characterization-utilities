from nomad.config.models.plugins import SchemaPackageEntryPoint
from pydantic import Field


class NewSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from characterization_nexus.schema_packages.schema_package import m_package

        return m_package


schema_package_entry_point = NewSchemaPackageEntryPoint(
    name='NewSchemaPackage',
    description='New schema package entry point configuration.',
)

class EmSchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from characterization_nexus.schema_packages.em_schema import m_package

        return m_package


em_schema_package_entry_point = EmSchemaPackageEntryPoint(
    name='EmSchemaPackage',
    description='New schema package entry point for electron microscopy to nexus.',
)
