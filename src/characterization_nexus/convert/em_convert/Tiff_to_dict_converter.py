import os
import re

import h5py
import numpy as np
import tifffile as tf

from characterization_nexus.convert.common import write_data


def extract_data_from_tif(tif_image):
    name = tif_image.split('/')[-1]
    name = name.split('.')[0]
    with tf.TiffFile(tif_image) as tiffile:
        arrays = []
        for i, page in enumerate(tiffile.pages):
            array = page.asarray()
            # Convertiamo in uint16 preservando il range
            if array.dtype != np.uint16:
                array = (array / array.max() * 65535).astype(np.uint16)
            arrays.append(array)
    return name, arrays


def search_quantities(text):
    tag_dict = {}
    pattern = r'([A-Z]\w+)\s*=\s*((?:(?!\\n)[^;,])+)'
    matches = re.findall(pattern, text)
    for name, value in matches:
        tag_dict[name] = value

    return tag_dict


def extract_metadata_from_tif(percorso):
    dictionar = {}
    with tf.TiffFile(percorso) as tiffile:
        dictionar['file_name'] = percorso.split('/')[-1]
        for i, page in enumerate(tiffile.pages):
            mio_dict = {}
            for tag in page.tags:
                try:
                    if (
                        isinstance(tag.value, str)
                        or isinstance(tag.value, float)
                        or isinstance(tag.value, int)
                    ):
                        mio_dict[tag.name] = tag.value
                    elif isinstance(tag.value, tuple):
                        mio_dict[tag.name] = list(tag.value)
                    elif isinstance(tag.value, bytes):
                        new = str(tag.value)
                        mio_dict |= search_quantities(new)
                    elif isinstance(tag.value, dict):
                        mio_dict[tag.name] = tag.value
                except Exception:
                    mio_dict[tag.name] = 'Non leggibile'
            dictionar[f'page_{i + 1}'] = mio_dict
    return dictionar


def get_nested(d: dict, path: str, default=None):
    keys = path.split('.')
    for k in keys:
        if not isinstance(d, dict) or k not in d:
            return default
        d = d[k]
    return d


def set_nested(d: dict, path: str, value):
    keys = path.split('.')
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = value


mapping = {
    'instrument.name': {
        'aliases': ['name', 'Device', 'FEI_HELIOS.System.SystemType', 'Strumento.nome']
    },
    'instrument.fabrication.model': {'aliases': ['model', 'DeviceModel']},
    'instrument.fabrication.manufacturer': {'aliases': ['manufacturer', 'Make']},
    'instrument.detector.type': {'aliases': ['Detector', 'FEI_HELIOS.Detectors.Name']},
    'instrument.program.program.program': {
        'aliases': ['Software', 'FEI_HELIOS.System.Software']
    },
    'instrument.program.program.version': {
        'aliases': ['SoftwareVersion', 'FEI_HELIOS.System.Software']
    },
    'instrument.ebeam_column.electron_source.emitter_type': {
        'aliases': ['FEI_HELIOS.EBeam.Source', 'Gun']
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
        'aliases': ['WD', 'FEI_HELIOS.EBeam.WD'],
        'unit': 'm',
    },
    'events.instrument.optics.probe_current': {
        'aliases': ['PredictedBeamCurrent', 'FEI_HELIOS.EBeam.BeamCurrent'],
        'unit': 'A',
    },
    'events.instrument.optics.tilt_correction': {
        'aliases': ['TiltCorrection', 'FEI_HELIOS.EBeam.TiltCorrectionIsOn'],
        'get': lambda x: (
            True
            if str(x).lower() == 'yes' or (isinstance(x, int | float) and x != 0)
            else False
        ),
    },
    'events.instrument.ebeam_column.operation_mode': {'aliases': ['ScanMode']},
    'events.instrument.ebeam_column.electron_source.voltage': {
        'aliases': ['AcceleratorVoltage', 'FEI_HELIOS.EBeam.HV'],
        'unit': 'V',
    },
    'events.instrument.ebeam_column.electron_source.emission_current': {
        'aliases': ['EmissionCurrent', 'FEI_HELIOS.EBeam.EmissionCurrent'],
        'unit': 'A',
    },
}


def try_parse_number(value: str):
    # Prova a convertire una stringa in int o float. Se non riesce, restituisce None.
    try:
        if '.' in value:
            return float(value)
        else:
            return int(value)
    except (ValueError, TypeError):
        return None


def generate_numeric_values(numeric_value, unit, output, target_path):
    if unit is not None:
        set_nested(output, target_path, {'value': numeric_value, 'unit': unit})
    else:
        set_nested(output, target_path, numeric_value)


def transform(input_dict: dict, mapping: dict) -> dict:
    output = {}
    for target_path, rules in mapping.items():
        aliases = rules.get('aliases', [])
        unit = rules.get('unit', None)
        metodo = rules.get('get', None)

        # Prima prova con gli aliases
        value_found = False
        for alias in aliases:
            value = get_nested(input_dict, alias)
            if value is not None:
                if isinstance(value, str) and value != '':
                    numeric_value = try_parse_number(value)
                    if numeric_value is not None:
                        generate_numeric_values(
                            numeric_value, unit, output, target_path
                        )
                        break
                    if metodo is not None:
                        new = metodo(value)
                        set_nested(output, target_path, new)
                        break
                    else:
                        # non parsabile -> salvo come stringa
                        set_nested(output, target_path, value)
                        break
                elif isinstance(value, int | float):
                    generate_numeric_values(value, unit, output, target_path)
                    break
                value_found = True
                break

        # Se non è stato trovato nessun valore negli aliases, prova con il metodo get
        if not value_found and metodo is not None:
            computed_value = metodo(input_dict)
            if computed_value is not None:
                if isinstance(computed_value, int | float):
                    generate_numeric_values(computed_value, unit, output, target_path)
                else:
                    set_nested(output, target_path, computed_value)
    set_nested(output, 'instrument.m_def', 'NXem_instrument')
    set_nested(output, 'instrument.fabrication.m_def', 'NXfabrication')
    set_nested(output, 'instrument.detector.m_def', 'NXdetector')
    set_nested(output, 'instrument.program.m_def', 'NXprogram')
    set_nested(output, 'instrument.ebeam_column.m_def', 'NXebeam_column')
    set_nested(output, 'instrument.ebeam_column.electron_source.m_def', 'NXsource')
    set_nested(output, 'events.m_def', 'NXem_event_data')
    set_nested(output, 'events.instrument.optics.m_def', 'NXem_optical_system')
    set_nested(output, 'events.instrument.m_def', 'NXem_instrument')
    set_nested(output, 'events.instrument.ebeam_column.m_def', 'NXebeam_column')
    set_nested(
        output, 'events.instrument.ebeam_column.electron_source.m_def', 'NXsource'
    )
    return output


def generate_metadata_array(tif_file):
    metadata = extract_metadata_from_tif(tif_file)
    outputs = []
    for i in range(0, len(metadata.keys())):
        output = {}
        if i == 0:
            pass
        else:
            output = transform(metadata[f'page_{i}'], mapping)
            outputs.append(output)
    return outputs


def write_measurement_section(where, tiff_file):
    metadati = generate_metadata_array(tiff_file)
    name, dati = extract_data_from_tif(tiff_file)
    if len(metadati) != len(dati):
        raise (
            'Data and metadata have not the same dimension, each image needs metadata'
        )
    else:
        for meta in metadati:
            write_data(meta, where)
        for idx, dat in enumerate(dati):
            image = where['events'].create_group(f'image_{idx}')
            image.attrs['NX_class'] = 'NXimage'
            image_2d = where['events'][f'image_{idx}'].create_group('image_2d')
            image_2d.attrs['NX_class'] = 'NXdata'
            image_2d.create_dataset('title', data=name)
            image_2d.create_dataset('real', data=dat, dtype='uint16')
            image_2d.create_dataset('axis_i', data=np.arange(dat.shape[0]))
            image_2d.create_dataset('axis_j', data=np.arange(dat.shape[1]))
            image_2d.attrs['signal'] = 'real'
            image_2d.attrs['axis_i_indices'] = 0
            image_2d.attrs['axis_j_indices'] = 1


def write_data_to_nexus(raw_path, data_file, output):
    with h5py.File(os.path.join(raw_path, output), 'a') as f:
        entry = f['entry']
        entry.attrs['default'] = '/entry/measurement/events/image_0/image_2d'
        meas = entry.create_group('measurement')
        meas.attrs['NX_class'] = 'NXem_measurement'
        write_measurement_section(meas, os.path.join(raw_path, data_file))
