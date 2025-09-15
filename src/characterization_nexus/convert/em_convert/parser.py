import h5py
import numpy as np
import tifffile as tf

from characterization_nexus.convert.common import write_data
from characterization_nexus.convert.em_convert.fei_helios_matcher import matching
from characterization_nexus.convert.em_convert.utils import (
    generate_numeric_values,
    get_nested,
    search_quantities,
    set_nested,
    try_parse_number,
)


# This function is able to extract from a multipage tiff an array of data for each image
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


# This function extracts metadata from each tiff and id needed convert quantities in
# type hashable or usabel as dictionar values.


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


# Funzione che infine restituisce il dizionario finale che ha una struttura come
# descritto nell'xml della microscopia elettronica
# (pynxtools/definitions/applications/NXem.nxdl.xml) che poi verrà passato alla funzione
# write_data in common per scrivere il nexus(o meglio aggiornarlo) nella sua parte di
# dati.


def transform(input_dict: dict, matching: dict) -> dict:
    output = {}
    for target_path, rules in matching.items():
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


# Questa serve qualora ogni pagina riporti metdati diversi e quindi è utile perché in
# combinazione con la funzione di parsing dei dati genera un'altra lista che avrà i
# metadati dell'immagine corrispondente allo stesso indice nella lista di arrays


def generate_metadata_array(tif_file):
    metadata = extract_metadata_from_tif(tif_file)
    outputs = []
    for i in range(0, len(metadata.keys())):
        output = {}
        if i == 0:
            pass
        else:
            output = transform(metadata[f'page_{i}'], matching)
            outputs.append(output)
    return outputs


# Funzione che finalmente scrive la sezione measurement con i dati parsati da quelle
# precedenti


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


# Infine la funzione che apre il file nexus(se già esistente lo aggiorna soltanto senza
# eliminare dati già esistenti) e richiama la funzione precedente.


def write_data_to_nexus(output, data_file):
    with h5py.File(output, 'a') as f:
        entry = f['entry']
        #        entry.attrs['default'] = '/entry/measurement/events/image_0/image_2d'
        meas = entry.create_group('measurement')
        meas.attrs['NX_class'] = 'NXem_measurement'
        write_measurement_section(meas, data_file)
