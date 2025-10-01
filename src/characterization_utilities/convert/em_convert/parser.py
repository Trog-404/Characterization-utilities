from pathlib import Path

import h5py
import numpy as np
import tifffile as tf
import tomllib
from PIL import Image as im

from characterization_utilities.convert.em_convert import load_matchers
from characterization_utilities.convert.em_convert.utils import (
    search_quantities,
)

pyproject_path = Path(__file__).resolve().parents[4] / 'pyproject.toml'

with pyproject_path.open('rb') as f:
    data = tomllib.load(f)

version = data['project']['version']
url = data['project']['urls']['Repository']

SUPPORTED_IMAGE_CHANNELS = 2

# This function will be used only for non tiff files to upload at least the image


def extract_data_from_image(image_file):
    name = image_file.split('/')[-1].split('.')[0]
    arrays = []
    with im.open(image_file) as img:
        i = 0
        while True:
            try:
                img.seek(i)
                arrays.append(np.array(img))
                i += 1
            except EOFError:
                break

    return name, arrays


def verify_if_is_tif(file, logger) -> bool:
    try:
        tf.imread(file)
        return True
    except tf.TiffFileError:
        logger.warning('No file tiff provided, base analysis will follow')
        return False
    except Exception as e:
        logger.error(f'Error during the opening of the file {file}: {e}')
        return False


# This function extracts metadata from each page in the tiff and id needed convert
# quantities in type hashable or reusable as dictionar values.


def extract_metadata_from_tif_page(tif_page) -> dict:
    mio_dict = {}
    for tag in tif_page.tags:
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
    return mio_dict


# This function finally allows to populate the measurement section taking a tiff file.
# Through a matching procedure for each fields required by the NeXus schema, taking the
# desired values from an input dictionar generated trough the
# extract_metadata_from_tif_page function and matching from some an ad hoc search
# defined for each field in the groups. See <nistrument_type>_matchers.py files.


def generate_2d_image(where, index, title, dati):
    image = where.create_group(f'image_{index}')
    image.attrs['NX_class'] = 'NXimage'
    image_2d = image.create_group('image_2d')
    image_2d.attrs['NX_class'] = 'NXdata'
    image_2d.create_dataset('title', data=title)
    image_2d.create_dataset('real', data=dati)
    image_2d.create_dataset('axis_i', data=np.arange(dati.shape[0]))
    image_2d.create_dataset('axis_j', data=np.arange(dati.shape[1]))
    image_2d.attrs['signal'] = 'real'
    image_2d.attrs['axis_i_indices'] = 0
    image_2d.attrs['axis_j_indices'] = 1


def tiff_parser(where, file_tiff, logger) -> None:
    if not verify_if_is_tif(file_tiff, logger):
        name, arrays = extract_data_from_image(file_tiff)
        for count, dati in enumerate(arrays):
            if len(dati.shape) > SUPPORTED_IMAGE_CHANNELS:
                logger.error(
                    f"""
                    File used {file_tiff} has RGB (or RGBA) channels. This format is
                    not supported. Convert to greyscale and retry.
                    """
                )
            index = f'{name}_{count}'
            matchers = load_matchers(None, logger)  # dummy call! They are matchers
            for matching in matchers:
                newgrp = matching.set_group(where, index, 0)
                matching.populate_not_repeatable_group(newgrp, {}, logger)
            generate_2d_image(where[f'event_{index}'], count, name, dati)
    else:
        with tf.TiffFile(file_tiff) as tif:
            for count, page in enumerate(tif.pages):
                name = file_tiff.split('/')[-1]
                name = name.split('.')[0]
                dati = page.asarray()
                if len(dati.shape) > SUPPORTED_IMAGE_CHANNELS:
                    logger.error(
                        f"""
                        File used {file_tiff} has RGB (or RGBA) channels. This format 
                        is not supported. Please convert to greyscale and retry.
                    """
                    )
                index = f'{name}_{count}'
                # Inserire qui una routine di controllo tipo dati
                matchers = load_matchers(page.tags, logger)
                metadata = extract_metadata_from_tif_page(page)
                if matchers is not None:
                    for matching in matchers:
                        if matching.check_repeatable(metadata, logger):
                            matching.generate_repeatable_groups(
                                where, index, metadata, logger
                            )
                        else:
                            newgrp = matching.set_group(where, index, 0)
                            matching.populate_not_repeatable_group(
                                newgrp, metadata, logger
                            )
                generate_2d_image(where[f'event_{index}'], count, name, dati)


# Infine la funzione che apre il file nexus(se già esistente lo aggiorna soltanto senza
# eliminare dati già esistenti) e richiama la funzione precedente. Moreover additional
# metadata informations like the profiling section is given.


def write_data_to_nexus_new(output, data_file, logger):
    with h5py.File(output, 'a') as f:
        entry = f['entry']
        meas = entry.require_group('measurement')
        meas.attrs['NX_class'] = 'NXem_measurement'
        try:
            prof = entry.create_group('profiling')
            prof.attrs['NX_class'] = 'NXcs_profiling'
            prog = prof.create_group('programID')
            prog.attrs['NX_class'] = 'NXprogram'
            prog.create_dataset('program', data='characterization_utilities')
            prog['program'].attrs['version'] = version
            prog['program'].attrs['url'] = url
        except ValueError:
            pass
        tiff_parser(meas, data_file, logger)
