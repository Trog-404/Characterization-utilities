from characterization_utilities.convert.em_convert.utils import (
    Matcher,
    SectionHeader,
    get_nested,
)

meas_instrument = Matcher(
    SectionHeader(path='./instrument/', type_class='NXem_instrument'),
    {'name': {'alias': 'FEI_HELIOS.System.SystemType'}},
)
instr_program = Matcher(
    SectionHeader(path='./instrument/program', type_class='NXprogram'),
    {'program': {'alias': 'FEI_HELIOS.System.Software'}},
)
meas_event = Matcher(SectionHeader(path='./eventID/', type_class='NXem_event_data'), {})
event_instrument = Matcher(
    SectionHeader(path='./eventID/instrument', type_class='NXem_instrument'), {}
)
event_instrument_optics = Matcher(
    SectionHeader(path='./eventID/instrument/optics', type_class='NXem_optical_system'),
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
        'tilt_correction': {
            'alias': 'FEI_HELIOS.EBeam.TiltCorrectionIsOn',
            'get': lambda x: (
                True
                if str(x).lower() == 'yes' or (isinstance(x, int | float) and x != 0)
                else False
            ),
        },
    },
)

instr_ebeam = Matcher(
    SectionHeader(path='./instrument/ebeam_column', type_class='NXebeam_column'),
    {},
)
ebeam_source = Matcher(
    SectionHeader(
        path='./instrument/ebeam_column/electron_source/',
        type_class='NXsource',
    ),
    {
        'emitter_type': {'alias': 'FEI_HELIOS.EBeam.Source'},
    },
)
event_instr_ebeam = Matcher(
    SectionHeader(
        path='./eventID/instrument/ebeam_column', type_class='NXebeam_column'
    ),
    {
        'operation_mode': {},
    },
)

event_instr_ebeam_source = Matcher(
    SectionHeader(
        path='./eventID/instrument/ebeam_column/electron_source/',
        type_class='NXsource',
    ),
    {
        'voltage': {'alias': 'FEI_HELIOS.EBeam.HV', 'unit': 'V'},
        'emission_current': {'alias': 'FEI_HELIOS.EBeam.EmissionCurrent', 'unit': 'A'},
    },
)

instr_detector = Matcher(
    SectionHeader(path='./instrument/detector/', type_class='NXdetector'),
    {'type': {'alias': 'FEI_HELIOS.Detectors.Name'}},
)


matchers = [
    meas_instrument,
    instr_program,
    meas_event,
    event_instrument_optics,
    event_instrument,
    instr_ebeam,
    ebeam_source,
    event_instr_ebeam,
    event_instr_ebeam_source,
    instr_detector,
]

### TODO Inserire descrizione degli attributi per i campi che lo richiedono
### TODO Inserire la compilazione atumatica del nome per sezioni ripetibili
