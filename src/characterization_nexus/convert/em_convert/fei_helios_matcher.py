from characterization_nexus.convert.em_convert.utils import (
    Matcher,
    SectionHeader,
    get_nested,
)

meas_instrument = Matcher(
    SectionHeader(path='./instrument/', name='', type_class='NXem_instrument'),
    {'name': {'alias': 'FEI_HELIOS.System.SystemType'}},
)
# instr_fabrication= Matcher(
#    SectionHeader(path= './instrument/fabrication/', type_class= 'NXfabrication'),
#    {'': {'alias': 'FEI_HELIOS.System.SystemType'}}
# )
instr_program = Matcher(
    SectionHeader(path='./instrument/program', name='', type_class='NXprogram'),
    {'program': {'alias': 'FEI_HELIOS.System.Software'}},
)
meas_event = Matcher(
    SectionHeader(path='./events/', name='', type_class='NXem_event_data'), {}
)
event_instrument = Matcher(
    SectionHeader(path='./events/instrument', name='', type_class='NXem_instrument'), {}
)
event_instrument_optics = Matcher(
    SectionHeader(
        path='./events/instrument/optics', name='', type_class='NXem_optical_system'
    ),
    {
        'magnification': {
            'get': lambda input_dict: (
                (w / h)
                if (w := get_nested(input_dict, 'FEI_HELIOS.Image.MagCanvasRealWidth'))
                and (h := get_nested(input_dict, 'FEI_HELIOS.Scan.HorFieldsize'))
                and h != 0
                else None
            )
        },
        'working_distance': {
            'alias': 'FEI_HELIOS.EBeam.WD',
            'unit': 'm',
        },
        'probe_current': {
            'alias': 'FEI_HELIOS.EBeam.BeamCurrent',
            'unit': 'A',
        },
        'events.instrument.optics.tilt_correction': {
            'alias': 'FEI_HELIOS.EBeam.TiltCorrectionIsOn',
            'get': lambda x: (
                True
                if str(x).lower() == 'yes' or (isinstance(x, int | float) and x != 0)
                else False
            ),
        },
    },
)

matchers = [
    meas_instrument,
    instr_program,
    meas_event,
    event_instrument_optics,
    event_instrument
]
# {
#    'instrument.detector.type': {'aliases': ['FEI_HELIOS.Detectors.Name']},
#    'instrument.program.program.program': {'aliases': ['FEI_HELIOS.System.Software']},
#    'instrument.program.program.version': {'aliases': ['FEI_HELIOS.System.Software']},
#    'instrument.ebeam_column.electron_source.emitter_type': {
#        'aliases': ['FEI_HELIOS.EBeam.Source']
#    },
#    'events.instrument.ebeam_column.operation_mode': {'aliases': []},
#    'events.instrument.ebeam_column.electron_source.voltage': {
#        'aliases': ['FEI_HELIOS.EBeam.HV'],
#        'unit': 'V',
#    },
#    'events.instrument.ebeam_column.electron_source.emission_current': {
#        'aliases': ['FEI_HELIOS.EBeam.EmissionCurrent'],
#        'unit': 'A',
#    },
# }
#
