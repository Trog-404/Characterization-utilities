#######################################################################################
#         FILE CON FUNZIONI UTILI NELLA GENERAZIONE DEI FILE NEXUS A PARTIRE          #
#                        DA JSON O DIZIONARI NON SERIALIZZATI                         #
#######################################################################################

import h5py
import numpy as np
from dateutil.parser import isoparse

from characterization_nexus.mappers import load_mapper_manager

# Funzioni utili per lavorare con i datetime e scriverli in nexus con un controllo sul
# tipo se è quello atteso

dt=h5py.string_dtype(encoding="utf-8")

def is_iso8601(s: str) -> bool:
    try:
        isoparse(s)
        return True
    except (ValueError, TypeError):
        return False

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

# Le prossime due funzioni servono per estrarre il nome della classe che si legge
# nelle sottosezioni per poi utilizzarlo nella definizione della classe nexus da usare
# nella traduzione e quindi per reindirizzare poi al corretto mapping.

def get_real_mdef(old_key: str) -> str:
    if ':' in str(old_key):
        new_key = str(old_key).split(':', 1)[1]
    else:
        new_key = str(old_key)
    return new_key.split('(', 1)[0]

def is_scalar(value) ->bool :
    if np.isscalar(value):
        return True
    elif isinstance(value, str):
        return True
    else:
        return False

# Questa funzione ci permette di scrivere correttamente i dati dalla struttura ad
# archivio di nomad alla struttura nexus. Quindi fondamentalmente è il building block
# con cui gli ELNs vengono tradotti in dati nexus.

def write_data_new(dati, where, mapper: dict, MM: dict) -> None:
    for el in dati:
        valore = getattr(dati, el)
        if valore is not None:
            mdef = get_real_mdef(valore)
            if is_scalar(valore):
                if el in mapper:
                    if is_iso8601(valore):
                        where.create_dataset(mapper[el], data=valore, dtype=dt)
                    else:
                        where.create_dataset(mapper[el], data=valore)
            elif 'SubSectionList' in type(valore).__name__:
                if mdef in MM.keys():
                    new_dati_list = list(valore)
                    for ndati in new_dati_list:
                        repos = create_group_to_fill(
                            MM[mdef]['NX_class'], where, ndati.name
                        )
                        write_data_new(ndati, repos, MM[mdef]['mapper'], MM)
            elif type(valore).__name__.endswith('SubSection'):
                if mdef in MM.keys():
                    for ndati in valore:
                        repos = create_group_to_fill(
                            MM[mdef]['NX_class'], where, ndati.name
                        )
                        write_data_new(ndati, repos, MM[mdef]['mapper'], MM)

# Funzione che richiama la precedente e che crea davvero il nexus generandone l'entry.


def instanciate_nexus(output_file, dati, nxdl: str) -> None:
    # carico il manager giusto
    MM = load_mapper_manager(nxdl)

    # l’entry mapper lo prendo dal manager
    # supponendo che tu abbia sempre una voce "Entry" o simile
    entry_mapper = MM.get("Entry", {}).get("mapper", None)
    if entry_mapper is None:
        raise RuntimeError(f"Nessun entry mapper definito per {nxdl}")
    with h5py.File(output_file, 'w') as f:
        entry = f.create_group('entry')
        entry.attrs['NX_class'] = 'NXentry'
        entry.create_dataset('definition', data=nxdl)
        if dati is not None:
            write_data_new(dati, entry, entry_mapper, MM)