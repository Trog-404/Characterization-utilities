#######################################################################################
#         FILE CON FUNZIONI UTILI NELLA GENERAZIONE DEI FILE NEXUS A PARTIRE          #
#               DA DIZIONARI O PER PARSARE GLI ARCHIVI DA CUI SI PARTE                #
#######################################################################################

from datetime import datetime

import h5py
import numpy as np

from characterization_utilities.mappers import load_mapper_manager

# Definizione utile per la scritture dei datetimes

dt = h5py.string_dtype(encoding='utf-8')


# La prossima funzione ci permette di generare i gruppi dei nostri file hdf5.


def create_group_to_fill(TYPE, where, name):
    group = where.create_group(name)
    group.attrs['NX_class'] = TYPE
    return group


# Adesso che sappiamo generare i gruppi possiamo in teoria preoccuparci di scrivere
# le quantità in questi gruppi. Prima però le prossime due funzioni saranno utili. La
# prima estrae il nome della classe che si legge nelle sottosezioni per poi utilizzarlo
# nella definizione della classe nexus da usare nella traduzione e quindi per
# reindirizzare poi al corretto mapping. La seconda invece evrifica se è un campo da
# scrivere come dataset nel nexus.


def get_real_mdef(obj: str) -> str:
    old_key = f'{obj}'
    if ':' in str(old_key):
        new_key = str(old_key).split(':', 1)[1]
    else:
        new_key = str(old_key)
    return new_key.split('(', 1)[0]


def is_a_field(value) -> bool:
    if np.isscalar(value):
        return True
    elif isinstance(value, str | datetime):
        return True
    else:
        return False


# Questa funzione ci permette di scrivere correttamente i dati dalla struttura ad
# archivio di nomad alla struttura nexus. Quindi fondamentalmente è il building block
# con cui gli ELNs vengono tradotti in dati nexus. Potremmo avere quantità stringa
# che vengono lette e scritte come dataset del gruppo (facendo solo attenzione al tipo,
# perché le date richiedono una precisa formattazione e ciò che viene da campi RichText
# ha una formattazione html). I valori numerici senza unità di misura possono essere
# trattati come le stringhe. Abbiamo poi la possibilità di avere grandezze scalari con
# unità di misura, oppure grandezze vettoriali (simili alle scalari ma con un versore
# direzione associato). Ci sono delle quantità che iniziano con m_ che non vogiamo né
# mappare né accedere ai valori altrimenti avremmo gravi bugs sul nostro NOMAD. Infine,
# ci potrebbero essere delle sezioni che dobbiamo mappare a sezioni NeXus e in quel
# caso una volta ottenuto il tipo lo usiamo per ottenere la classe NeXus corrispondente
# dal mapper menager e richiamare la giusta routine di mapping.


def write_data(dati, where, mapper: dict, MM: dict, logger) -> None:
    for el in dati:
        val = dati[el]
        if val is not None:
            if is_a_field(val):
                if el in mapper:
                    if isinstance(val, datetime):
                        val = str(val)
                        where.create_dataset(mapper[el], data=val, dtype=dt)
                    elif isinstance(val, str) and ('<p>' in val or '</p>' in val):
                        val = val.replace('<p>', '').replace('</p>', '')
                        where.create_dataset(mapper[el], data=val)
                    else:
                        where.create_dataset(mapper[el], data=val)
            elif not el.startswith('m_'):
                mdef = get_real_mdef(val)
                if mdef in MM.keys():
                    if 'SubSectionList' in type(val).__name__:
                        new_dati_list = list(val)
                        for ndati in new_dati_list:
                            repos = create_group_to_fill(
                                MM[mdef]['NX_class'], where, ndati.name
                            )
                            write_data(
                                ndati.__dict__, repos, MM[mdef]['mapper'], MM, logger
                            )
                    elif type(val).__name__.endswith(mdef):
                        repos = create_group_to_fill(MM[mdef]['NX_class'], where, el)
                        write_data(val.__dict__, repos, MM[mdef]['mapper'], MM, logger)


# Funzione che richiama la precedente e che crea davvero il nexus generandone l'entry.


def instanciate_nexus(output_file, dati, nxdl: str, logger) -> None:
    # carico il manager giusto
    MM = load_mapper_manager(nxdl)
    # l’entry mapper lo prendo dal manager
    # supponendo che tu abbia sempre una voce "Entry" o simile
    entry_mapper = MM.get('Entry', {}).get('mapper', None)
    if entry_mapper is None:
        raise RuntimeError(f'Nessun entry mapper definito per {nxdl}')
    with h5py.File(output_file, 'w') as f:
        entry = f.create_group('entry')
        entry.attrs['NX_class'] = 'NXentry'
        entry.create_dataset('definition', data=nxdl)
        if dati is not None:
            write_data(dati, entry, entry_mapper, MM, logger)


# Supporto quantità vettoriali rimosso da rivedere
