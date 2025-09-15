from characterization_nexus.convert.em_convert.utils import get_nested

matching = {
    'instrument.name': {'aliases': ['name', 'FEI_HELIOS.System.SystemType']},
    'instrument.fabrication.model': {'aliases': ['model']},
    'instrument.fabrication.manufacturer': {'aliases': ['manufacturer']},
    'instrument.detector.type': {'aliases': ['FEI_HELIOS.Detectors.Name']},
    'instrument.program.program.program': {'aliases': ['FEI_HELIOS.System.Software']},
    'instrument.program.program.version': {'aliases': ['FEI_HELIOS.System.Software']},
    'instrument.ebeam_column.electron_source.emitter_type': {
        'aliases': ['FEI_HELIOS.EBeam.Source']
    },
    'events.instrument.optics.magnification': {
        'aliases': ['Magnification'],
        'get': lambda input_dict: (
            get_nested(input_dict, 'FEI_HELIOS.Image.MagCanvasRealWidth')
            / get_nested(input_dict, 'FEI_HELIOS.Scan.HorFieldsize')
            if get_nested(input_dict, 'FEI_HELIOS.Image.MagCanvasRealWidth') is not None
            and get_nested(input_dict, 'FEI_HELIOS.Scan.HorFieldsize') is not None
            and get_nested(input_dict, 'FEI_HELIOS.Scan.HorFieldsize') != 0
            else None
        ),
    },
    'events.instrument.optics.working_distance': {
        'aliases': ['FEI_HELIOS.EBeam.WD'],
        'unit': 'm',
    },
    'events.instrument.optics.probe_current': {
        'aliases': ['FEI_HELIOS.EBeam.BeamCurrent'],
        'unit': 'A',
    },
    'events.instrument.optics.tilt_correction': {
        'aliases': ['FEI_HELIOS.EBeam.TiltCorrectionIsOn'],
        'get': lambda x: (
            True
            if str(x).lower() == 'yes' or (isinstance(x, int | float) and x != 0)
            else False
        ),
    },
    'events.instrument.ebeam_column.operation_mode': {'aliases': []},
    'events.instrument.ebeam_column.electron_source.voltage': {
        'aliases': ['FEI_HELIOS.EBeam.HV'],
        'unit': 'V',
    },
    'events.instrument.ebeam_column.electron_source.emission_current': {
        'aliases': ['FEI_HELIOS.EBeam.EmissionCurrent'],
        'unit': 'A',
    },
}
