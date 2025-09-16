from nomad.config.models.plugins import ExampleUploadEntryPoint

example_upload_entry_point = ExampleUploadEntryPoint(
    title='Electron Microscopy',
    category='New NeXuS Examples',
    description="""
        This example upload show the method of storing raw data in nomad for electron
        microscopy experiments and from them producing a NeXuS file. This should be
        help a FAIR pipeline for data stored in Nomad.
    """,
    resources=['example_uploads/getting_started/*'],
)
