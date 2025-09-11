#######################################################################################
#         FILE CON FUNZIONI UTILI NELLA GENERAZIONE DEI FILE NEXUS A PARTIRE          #
#                        DA JSON O DIZIONARI NON SERIALIZZATI                         #
#######################################################################################
import json
import os
from pathlib import Path

import h5py
import numpy as np

from characterization_nexus.mappers import class_mapper as cmap
from characterization_nexus.mappers import entry_mapper as emap

# La prossima funzione ci permette di generare i gruppi dei nostri file hdf5
# leggendo la struttura dei json i quali saranno del tipo:
# {
#     "a": str,
#     "b": {
#         "value": number,
#         "unit": str
#     },
#     "c": {
#         "m_def": "NX_class",
#         "name":str,
#         ...
#     },
#     "d": {
#         "value": str,
#         "attr1": str,
#         "attr2": str
#     }
# }
# La funzione in pratica verrà usata quando raggiungendo il livello di "c" userà
# "c" per nominare il gruppo (infatti le chiavi dei json sono costruite in base
# a ciò che si aspetta il file nexus) e userà l'oggetto in "m_def" per prendere
# il TYPE. La posizione va assegnata tramite il where.


def create_group_to_fill(TYPE, where, name):
    group = where.create_group(name)
    group.attrs['NX_class'] = TYPE
    return group


# Adesso che sappiamo generare i gruppi possiamo in teoria preoccuparci di scrivere
# le quantità in questi gruppi. Potremmo avere quantità stringa (le più semplici)
# che vengono lette e scritte come dataset del gruppo. I valori numerici senza unità
# di misura possono essere trattati come le stringhe. Abbiamo poi la possibilità di
# avere grandezze scalari con unità di misura, oppure grandezze vettoriali (simili
# alle scalari ma con un versore direzione associato). Datasets di tipo stringa con
# attributi da inserire verranno scritti nella forma dizionario in cui il primo valore
# dovrà essere il valore del dataset e i successivi saranno tutti usati come attributi.
# Infine potremmo trovare altri gruppi come elementi di un altro gruppo per cui quando
# arriviamo a quel punto usiamo "m_def" come spiegato prima per generare un altro gruppo
# dentro il gruppo in cui stiamo lavorando (l'attuale where) e riprocediamo a scriverne
# le quantità modificando i dati che scrviamo (quelli del nuovo gruppo salvati da
# dati[row]) e scrivendoli nel gruppo restituito dalla funzione precedente. Iteriamo
# fino al completamento del json.


def write_data(dati, where):
    for row in dati:
        if isinstance(dati[row], str | int | float | bool) and row != 'm_def':
            where.create_dataset(row, data=dati[row])
        elif isinstance(dati[row], dict):
            if dati[row].keys() == {'value', 'unit', 'direction'}:
                where.create_dataset(row, data=dati[row]['value'])
                where[row].attrs['units'] = dati[row]['unit']
                where[row].attrs['direction'] = dati[row]['direction']
            elif dati[row].keys() <= {'value', 'unit'}:
                where.create_dataset(row, data=dati[row]['value'])
                where[row].attrs['units'] = dati[row]['unit']
            elif (
                all(isinstance(x, str) for x in dati[row].values())
                and 'm_def' not in dati[row]
            ):
                values = list(dati[row].values())
                keys = list(dati[row].keys())
                nome_dataset = keys[0]
                valore_dataset = values[0]
                where.create_dataset(nome_dataset, data=valore_dataset)
                for attr, inst in zip(keys[1:], values[1:]):
                    where[nome_dataset].attrs[attr] = inst
            elif 'm_def' in dati[row].keys():
                newwhere = create_group_to_fill(dati[row]['m_def'], where, row)
                write_data(dati[row], newwhere)


# Piccola funzione per leggere e caricare il contenuto di un json come dati


def write_from_json(json_input, where):
    with open(json_input, encoding='utf-8') as file:
        dati = json.load(file)
        write_data(dati, where)


# Funzione per aprire json multipli avendo comunque cura di aprire per primo il file
# contenente le informazioni dell'entry (il top level dei nostri nexus). E poi dovendo
# dare sempre un sample, uno strumento e uno user generiamo a monte i gruppi per quelle
# sottoentries così non serve m_def a inizio di ogni file.


def write_from_multiple_jsons(directory, entry):
    for file in os.listdir(directory):
        if Path(file).suffix == '.json' and 'entry' in file:
            write_from_json(os.path.join(directory, file), entry)

    for file in os.listdir(directory):
        if Path(file).suffix == '.json' and 'sample' in file:
            sample = create_group_to_fill('NXsample', entry, 'sample')
            write_from_json(os.path.join(directory, file), sample)
        if Path(file).suffix == '.json' and 'user' in file:
            user = create_group_to_fill('NXuser', entry, 'user')
            write_from_json(os.path.join(directory, file), user)
        if Path(file).suffix == '.json' and 'instrument' in file:
            instr = create_group_to_fill('NXinstrument', entry, 'instrument')
            write_from_json(os.path.join(directory, file), instr)


def write_additional_from_list(raw_path, file_list, output):
    with h5py.File(os.path.join(raw_path, output), 'a') as f:
        entry = f['entry']
        for file in file_list:
            if Path(file).suffix == '.json' and 'entry' in file:
                write_from_json(os.path.join(raw_path, file), entry)

        for file in file_list:
            if Path(file).suffix == '.json' and 'sample' in file:
                sample = create_group_to_fill('NXsample', entry, 'sample')
                write_from_json(os.path.join(raw_path, file), sample)
            if Path(file).suffix == '.json' and 'user' in file:
                user = create_group_to_fill('NXuser', entry, 'user')
                write_from_json(os.path.join(raw_path, file), user)
            if Path(file).suffix == '.json' and 'instrument' in file:
                instr = create_group_to_fill('NXinstrument', entry, 'instrument')
                write_from_json(os.path.join(raw_path, file), instr)


def write_scalar_value(valore, nome, where):
    if valore is not None:
        if isinstance(valore, str | float | int | bool):
            where.create_dataset(nome, data=valore)


def write_data_new(dati, where, mapper: dict) -> None:
    for el in dati:
        if el in mapper:
            valore = getattr(dati, el)
            if np.isscalar(valore):
                write_scalar_value(valore, mapper[el], where)
            else:
                pass


def instanciate_nexus(output_file, dati) -> None:
    with h5py.File(output_file, 'w') as f:
        entry = f.create_group('entry')
        entry.attrs['NX_class'] = 'NXentry'
        if dati is not None:
            write_data_new(dati, entry, emap)


def get_real_mdef(old_key: str) -> str:
    if ':' in str(old_key):
        new_key = str(old_key).split(':', 1)[1]
    else:
        new_key = str(old_key)
    return new_key.split('(', 1)[0]


def write_sub_from_nomad(output_file, dati, mapper: dict) -> None:
    with h5py.File(output_file, 'a') as f:
        entry = f['entry']
        group = entry.create_group(f'{dati.name}')
        key = get_real_mdef(str(dati))
        group.attrs['NX_class'] = cmap[key]
        write_data_new(dati, group, mapper)
