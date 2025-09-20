from characterization_utilities.convert.em_convert.utils import (
    Matcher,
    SectionHeader,
    get_nested,
)

meas_instrument = Matcher(
    SectionHeader(
        path='./instrument/', type_class='NXem_instrument', is_repeatable=False
    ),
    {
        'fields': {
            'name': {'alias': 'FEI_HELIOS.System.SystemType'},
            'type': {'alias': 'FEI_HELIOS.System.Type'},
        }
    },
)
meas_instr_detector = Matcher(
    SectionHeader(
        path='./instrument/detector*/',
        type_class='NXdetector',
        is_repeatable=(
            lambda input_dict: (
                True
                if get_nested(input_dict, 'FEI_HELIOS.Detectors.Name') == 'Mix'
                else False
            )
        ),
    ),
    {
        'src': 'FEI_HELIOS.Mix',
        'fields': {'name': {'alias': 'FEI_HELIOS.Detectors.Name'}},
        'repeatable_fields': {'name': r'Detector\d+$'},
    },
)
instr_program = Matcher(
    SectionHeader(
        path='./instrument/program', type_class='NXprogram', is_repeatable=False
    ),
    {
        'fields': {
            'program': {
                'alias': 'FEI_HELIOS.System.Software',
                'attributes': {'version': 'FEI_HELIOS.System.BuildNr'},
            }
        }
    },
)
instr_ebeam = Matcher(
    SectionHeader(
        path='./instrument/ebeam_column',
        type_class='NXebeam_column',
        is_repeatable=False,
    ),
    {},
)
instr_ebeam_fabr = Matcher(
    SectionHeader(
        path='./instrument/ebeam_column/fabrication',
        type_class='NXfabrication',
        is_repeatable=False,
    ),
    {
        'fields': {
            'model': {'alias': 'FEI_HELIOS.EBeam.ColumnType'},
            'vendor': {'alias': 'FEI_HELIOS.System.Column'},
        }
    },
)
ebeam_source = Matcher(
    SectionHeader(
        path='./instrument/ebeam_column/electron_source/',
        type_class='NXsource',
        is_repeatable=False,
    ),
    {
        'fields': {
            'emitter_type': {'alias': 'FEI_HELIOS.EBeam.Source'},
            'probe': {'get': lambda x: 'electron'},
        }
    },
)
meas_event = Matcher(
    SectionHeader(path='./eventID/', type_class='NXem_event_data', is_repeatable=False),
    {},
)
event_instrument = Matcher(
    SectionHeader(
        path='./eventID/instrument', type_class='NXem_instrument', is_repeatable=False
    ),
    {},
)
event_instrument_optics = Matcher(
    SectionHeader(
        path='./eventID/instrument/optics',
        type_class='NXem_optical_system',
        is_repeatable=False,
    ),
    {
        'fields': {
            'magnification': {
                'get': lambda input_dict: (
                    (w / h)
                    if (
                        w := get_nested(
                            input_dict, 'FEI_HELIOS.Image.MagCanvasRealWidth'
                        )
                    )
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
                'get': (lambda x: True if str(x).lower() == 'yes' else False),
            },
        }
    },
)
event_instr_ebeam = Matcher(
    SectionHeader(
        path='./eventID/instrument/ebeam_column',
        type_class='NXebeam_column',
        is_repeatable=False,
    ),
    {
        'fields': {
            'operation_mode': {'alias': 'FEI_HELIOS.EBeam.BeamMode'},
        }
    },
)

event_instr_ebeam_source = Matcher(
    SectionHeader(
        path='./eventID/instrument/ebeam_column/electron_source/',
        type_class='NXsource',
        is_repeatable=False,
    ),
    {
        'fields': {
            'voltage': {'alias': 'FEI_HELIOS.EBeam.HV', 'unit': 'V'},
            'emission_current': {
                'alias': 'FEI_HELIOS.EBeam.EmissionCurrent',
                'unit': 'A',
            },
        }
    },
)

matchers = [
    meas_instrument,
    meas_instr_detector,
    instr_program,
    instr_ebeam,
    instr_ebeam_fabr,
    ebeam_source,
    meas_event,
    event_instrument,
    event_instr_ebeam,
    event_instr_ebeam_source,
    event_instrument_optics,
]
