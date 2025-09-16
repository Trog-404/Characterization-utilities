from nomad.config.models.plugins import SchemaPackageEntryPoint


class EmSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from characterization_nexus.schema_packages.em_schema import m_package

        return m_package


em_schema_package_entry_point = EmSchemaPackageEntryPoint(
    name='EmSchemaPackage',
    description='New schema package entry point for electron microscopy to nexus.',
)
