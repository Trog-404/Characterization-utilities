from characterization_utilities.convert.em_convert.utils import (
    Matcher,
    SectionHeader,
    get_nested,
)

meas_instr_fabr = Matcher(
    SectionHeader(
        path='./instrument/fabrication/',
        type_class='NXfabrication',
        is_repeatable=False,
    ),
    {
        'fields': {
            'vendor': {'get': (lambda x: 'ThermoFisher')},
            'model': {'alias': 'FEI_HELIOS.System.Dnumber'},
        }
    },
)
meas_instr_program = Matcher(
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
event_instr_detector = Matcher(
    SectionHeader(
        path='./eventID/instrument/detector*/',
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
matchers_base = [
    meas_instr_fabr,
    meas_instr_program,
    meas_event,
    event_instrument,
    event_instr_detector,
]

### EBEAM MATCHERS

meas_instrument_ebeam = Matcher(
    SectionHeader(
        path='./instrument/', type_class='NXem_instrument', is_repeatable=False
    ),
    {
        'fields': {
            'name': {'alias': 'FEI_HELIOS.System.SystemType'},
            'type': {'get': (lambda x: 'sem')},
        }
    },
)

event_instrument_optics_ebeam = Matcher(
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
event_instr_ebeam_lens = Matcher(
    SectionHeader(
        path='./eventID/instrument/ebeam_column/final_lens/',
        type_class='NXelectromagnetic_lens',
        is_repeatable=False,
    ),
    {
        'fields': {
            'mode': {'alias': 'FEI_HELIOS.EBeam.LensMode'},
        }
    },
)
event_instr_ebeam_scan = Matcher(
    SectionHeader(
        path='./eventID/instrument/ebeam_column/scan_controller/',
        type_class='NXscan_controller',
        is_repeatable=False,
    ),
    {'fields': {'dwell_time': {'alias': 'FEI_HELIOS.Scan.Dwelltime'}}},
)

meas_instr_ebeam = Matcher(
    SectionHeader(
        path='./instrument/ebeam_column',
        type_class='NXebeam_column',
        is_repeatable=False,
    ),
    {},
)
meas_instr_ebeam_fabr = Matcher(
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
meas_instr_ebeam_lens = Matcher(
    SectionHeader(
        path='./instrument/ebeam_column/final_lens/',
        type_class='NXelectromagnetic_lens',
        is_repeatable=False,
    ),
    {'fields': {'name': {'alias': 'FEI_HELIOS.System.FinalLens'}}},
)
meas_instr_ebeam_lens_fabr = Matcher(
    SectionHeader(
        path='./instrument/ebeam_column/final_lens/fabrication',
        type_class='NXfabrication',
        is_repeatable=False,
    ),
    {'fields': {'vendor': {'alias': 'FEI_HELIOS.System.FinalLens'}}},
)
meas_instr_ebeam_scan = Matcher(
    SectionHeader(
        path='./instrument/ebeam_column/scan_controller',
        type_class='NXscan_controller',
        is_repeatable=False,
    ),
    {},
)
meas_instr__ebeam_scan_fabr = Matcher(
    SectionHeader(
        path='./instrument/ebeam_column/scan_controller/fabrication',
        type_class='NXfabrication',
        is_repeatable=False,
    ),
    {'fields': {'model': {'alias': 'FEI_HELIOS.System.Scan'}}},
)
meas_instr_ebeam_source = Matcher(
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

ebeam_matchers = [
    event_instrument_optics_ebeam,
    event_instr_ebeam,
    event_instr_ebeam_source,
    event_instr_ebeam_lens,
    event_instr_ebeam_scan,
    meas_instrument_ebeam,
    meas_instr_ebeam,
    meas_instr_ebeam_fabr,
    meas_instr_ebeam_lens,
    meas_instr_ebeam_lens_fabr,
    meas_instr_ebeam_scan,
    meas_instr__ebeam_scan_fabr,
    meas_instr_ebeam_source,
]

### IBEAM MATCHERS

meas_instrument_ibeam = Matcher(
    SectionHeader(
        path='./instrument/', type_class='NXem_instrument', is_repeatable=False
    ),
    {
        'fields': {
            'name': {'alias': 'FEI_HELIOS.System.SystemType'},
            'type': {'get': (lambda x: 'fib')},
        }
    },
)

meas_instr_ibeam = Matcher(
    SectionHeader(
        path='./instrument/ibeam_column/',
        type_class='NXibeam_column',
        is_repeatable=False,
    ),
    {},
)

meas_instr_ibeam_fabr = Matcher(
    SectionHeader(
        path='./instrument/ibeam_column/fabrication',
        type_class='NXfabrication',
        is_repeatable=False,
    ),
    {
        'fields': {
            'model': {'alias': 'FEI_HELIOS.IBeam.ColumnType'},
            'vendor': {'alias': 'FEI_HELIOS.System.Column'},
        }
    },
)
meas_instr_ibeam_source = Matcher(
    SectionHeader(
        path='./instrument/ibeam_column/ion_source/',
        type_class='NXsource',
        is_repeatable=False,
    ),
    {'fields': {'type': {'get': (lambda x: 'Ion Source')}}},
)
meas_instr_ebeam_source_probe = Matcher(
    SectionHeader(
        path='./instrument/ibeam_column/ion_source/probe',
        type_class='NXatom',
        is_repeatable=False,
    ),
    {
        'fields': {
            'name': {'alias': 'FEI_HELIOS.IBeam.Source'},
        }
    },
)
meas_instr_ibeam_lens = Matcher(
    SectionHeader(
        path='./instrument/ibeam_column/final_lens/',
        type_class='NXelectromagnetic_lens',
        is_repeatable=False,
    ),
    {'fields': {'name': {'alias': 'FEI_HELIOS.System.FinalLens'}}},
)
meas_instr_ibeam_lens_fabr = Matcher(
    SectionHeader(
        path='./instrument/ibeam_column/final_lens/fabrication',
        type_class='NXfabrication',
        is_repeatable=False,
    ),
    {'fields': {'vendor': {'alias': 'FEI_HELIOS.System.FinalLens'}}},
)
meas_instr_ibeam_scan = Matcher(
    SectionHeader(
        path='./instrument/ibeam_column/scan_controller',
        type_class='NXscan_controller',
        is_repeatable=False,
    ),
    {},
)
meas_instr__ibeam_scan_fabr = Matcher(
    SectionHeader(
        path='./instrument/ibeam_column/scan_controller/fabrication',
        type_class='NXfabrication',
        is_repeatable=False,
    ),
    {'fields': {'model': {'alias': 'FEI_HELIOS.System.Scan'}}},
)
event_instrument_optics_ibeam = Matcher(
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
                'alias': 'FEI_HELIOS.IBeam.WD',
                'unit': 'm',
            },
            'probe_current': {
                'alias': 'FEI_HELIOS.IBeam.BeamCurrent',
                'unit': 'A',
            },
            'tilt_correction': {
                'alias': 'FEI_HELIOS.IBeam.TiltCorrectionIsOn',
                'get': (lambda x: True if str(x).lower() == 'yes' else False),
            },
        }
    },
)
event_instr_ibeam = Matcher(
    SectionHeader(
        path='./eventID/instrument/ibeam_column',
        type_class='NXibeam_column',
        is_repeatable=False,
    ),
    {
        'fields': {
            'operation_mode': {'alias': 'FEI_HELIOS.IBeam.BeamMode'},
        }
    },
)

event_instr_ibeam_source = Matcher(
    SectionHeader(
        path='./eventID/instrument/ibeam_column/ion_source/',
        type_class='NXsource',
        is_repeatable=False,
    ),
    {'fields': {'voltage': {'alias': 'FEI_HELIOS.IBeam.HV', 'unit': 'V'}}},
)
event_instr_ibeam_source_probe = Matcher(
    SectionHeader(
        path='./eventID/instrument/ibeam_column/ion_source/probe',
        type_class='NXatom',
        is_repeatable=False,
    ),
    {
        'fields': {
            'name': {'alias': 'FEI_HELIOS.IBeam.Source'},
        }
    },
)
event_instr_ibeam_lens = Matcher(
    SectionHeader(
        path='./eventID/instrument/ibeam_column/final_lens/',
        type_class='NXelectromagnetic_lens',
        is_repeatable=False,
    ),
    {
        'fields': {
            'mode': {'alias': 'FEI_HELIOS.IBeam.LensMode'},
        }
    },
)
event_instr_ibeam_scan = Matcher(
    SectionHeader(
        path='./eventID/instrument/ibeam_column/scan_controller/',
        type_class='NXscan_controller',
        is_repeatable=False,
    ),
    {'fields': {'dwell_time': {'alias': 'FEI_HELIOS.Scan.Dwelltime'}}},
)

ibeam_matchers = [
    event_instrument_optics_ibeam,
    event_instr_ibeam,
    event_instr_ibeam_source,
    event_instr_ibeam_source_probe,
    event_instr_ibeam_lens,
    event_instr_ibeam_scan,
    meas_instrument_ibeam,
    meas_instr_ibeam,
    meas_instr_ibeam_fabr,
    meas_instr_ibeam_source,
    meas_instr_ibeam_lens,
    meas_instr_ibeam_lens_fabr,
    meas_instr_ibeam_scan,
    meas_instr__ibeam_scan_fabr,
]


def get_matchers(metadata: dict) -> list:
    """Ritorna i matchers giusti in base ai metadati"""
    if get_nested(metadata, 'FEI_HELIOS.Beam.Beam') == 'EBeam':
        return matchers_base + ebeam_matchers
    elif get_nested(metadata, 'FEI_HELIOS.Beam.Beam') == 'IBeam':
        return matchers_base + ibeam_matchers
