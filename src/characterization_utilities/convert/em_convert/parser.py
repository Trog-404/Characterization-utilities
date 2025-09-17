import h5py
import numpy as np
import tifffile as tf

from characterization_utilities.convert.em_convert import load_matchers
from characterization_utilities.convert.em_convert.utils import (
    search_quantities,
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


# Funzione che finalmente scrive la sezione measurement con i dati parsati da quelle
# precedenti


def write_measurement_section(where, tiff_file):
    metadata = extract_metadata_from_tif(tiff_file)
    matchers = load_matchers('FEI_HELIOS')
    for i in range(0, len(metadata.keys())):
        if i == 0:
            pass
        else:
            for matching in matchers:
                newgrp = matching.set_group(where)
                matching.populate_group(newgrp, metadata[f'page_{i}'])
    name, dati = extract_data_from_tif(tiff_file)
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
