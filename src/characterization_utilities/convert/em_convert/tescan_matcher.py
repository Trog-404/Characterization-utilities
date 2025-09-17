matching = {
    'instrument.name': {'aliases': ['name', 'Device']},
    'instrument.fabrication.model': {'aliases': ['model', 'DeviceModel']},
    'instrument.fabrication.manufacturer': {'aliases': ['manufacturer', 'Make']},
    'instrument.detector.type': {'aliases': ['Detector']},
    'instrument.program.program.program': {'aliases': ['Software']},
    'instrument.program.program.version': {'aliases': ['SoftwareVersion']},
    'instrument.ebeam_column.electron_source.emitter_type': {'aliases': ['Gun']},
    'events.instrument.optics.magnification': {'aliases': ['Magnification']},
    'events.instrument.optics.working_distance': {
        'aliases': ['WD'],
        'unit': 'm',
    },
    'events.instrument.optics.probe_current': {
        'aliases': ['PredictedBeamCurrent'],
        'unit': 'A',
    },
    'events.instrument.optics.tilt_correction': {
        'aliases': ['TiltCorrection'],
        'get': lambda x: (
            True
            if str(x).lower() == 'yes' or (isinstance(x, int | float) and x != 0)
            else False
        ),
    },
    'events.instrument.ebeam_column.operation_mode': {'aliases': ['ScanMode']},
    'events.instrument.ebeam_column.electron_source.voltage': {
        'aliases': ['AcceleratorVoltage'],
        'unit': 'V',
    },
    'events.instrument.ebeam_column.electron_source.emission_current': {
        'aliases': ['EmissionCurrent'],
        'unit': 'A',
    },
}
