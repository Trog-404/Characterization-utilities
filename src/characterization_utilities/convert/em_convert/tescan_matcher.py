import re

from characterization_utilities.convert.em_convert.utils import (
    Matcher,
    SectionHeader,
    get_nested,
)

meas_instrument = Matcher(
    SectionHeader(
        path='./instrument/', type_class='NXem_instrument', is_repeatable=False
    ),
    {'fields': {'name': {'alias': 'Device'}, 'type': {'alias': 'AccType'}}},
)
meas_instr_fabr = Matcher(
    SectionHeader(
        path='./instrument/fabrication/',
        type_class='NXfabrication',
        is_repeatable=False,
    ),
    {
        'fields': {
            'vendor': {'alias': 'Make'},
            'model': {'alias': 'DeviceModel'},
            'serial_number': {'alias': 'SerialNumber'},
        }
    },
)
instr_program = Matcher(
    SectionHeader(
        path='./instrument/program', type_class='NXprogram', is_repeatable=False
    ),
    {
        'fields': {
            'program': {
                'alias': 'Software',
            }
        }
    },
)
event_instr_detector = Matcher(
    SectionHeader(
        path='./eventID/instrument/detector*/',
        type_class='NXdetector',
        is_repeatable=lambda input_dict: (
            sum(1 for x in input_dict if re.match(r'Detector\d+$', x)) > 1
        ),
    ),
    {
        'fields': {'name': {'alias': 'Detector0'}},
        'repeatable_fields': {'name': r'Detector\d+$'},
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
ebeam_source = Matcher(
    SectionHeader(
        path='./instrument/ebeam_column/electron_source/',
        type_class='NXsource',
        is_repeatable=False,
    ),
    {
        'fields': {
            'emitter_type': {'alias': 'Gun'},
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
event_instr_optics = Matcher(
    SectionHeader(
        path='./eventID/instrument/optics',
        type_class='NXem_optical_system',
        is_repeatable=False,
    ),
    {
        'fields': {
            'magnification': {'alias': 'Magnification'},
            'working_distance': {
                'alias': 'WD',
                'unit': 'm',
            },
            'probe_current': {
                'alias': 'PredictedBeamCurrent',
                'unit': 'A',
            },
            'tilt_correction': {
                'alias': 'TiltCorrection',
                'get': (lambda x: True if x != 0 else False),
            },
            'field_of_view': {
                'get': lambda x: (
                    (w / counts)
                    if (
                        w := (
                            float(get_nested(x, 'ImageWidth'))
                            * float(get_nested(x, 'PixelSizeX'))
                        )
                    )
                    and (counts := float(get_nested(x, 'ViewFieldsCountX')))
                    else None
                )
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
            'operation_mode': {'alias': 'ScanMode'},
        }
    },
)

event_instr_ebeam_scan = Matcher(
    SectionHeader(
        path='./eventID/instrument/ebeam_column/scan_controller',
        type_class='NXscan_controller',
        is_repeatable=False,
    ),
    {'fields': {'dwell_time': {'alias': 'DwellTime'}}},
)

event_instr_ebeam_source = Matcher(
    SectionHeader(
        path='./eventID/instrument/ebeam_column/electron_source/',
        type_class='NXsource',
        is_repeatable=False,
    ),
    {
        'fields': {
            'voltage': {'alias': 'HV', 'unit': 'V'},
            'emission_current': {
                'alias': 'EmissionCurrent',
                'unit': 'A',
            },
        }
    },
)

matchers = [
    meas_instrument,
    meas_instr_fabr,
    event_instr_detector,
    instr_program,
    instr_ebeam,
    ebeam_source,
    meas_event,
    event_instrument,
    event_instr_ebeam,
    event_instr_ebeam_scan,
    event_instr_ebeam_source,
    event_instr_optics,
]
