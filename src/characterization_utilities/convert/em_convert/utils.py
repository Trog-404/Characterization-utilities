import re
from collections.abc import Callable

from pydantic import BaseModel

# This function is useful if for some reasons tags from the dict are stored in a single
# text that needs to be parsed. For example if we have metadata written as 'tag1=value1
# \n tag2=value' we are able to split the two tags with the relative values as
# {tag1: value1, tag2: value2}


def search_quantities(text):
    tag_dict = {}
    pattern = r'([A-Z]\w+)\s*=\s*((?:(?!\\n)[^;,])+)'
    matches = re.findall(pattern, text)
    for name, value in matches:
        tag_dict[name] = value

    return tag_dict


# Necessatio in combinazione con la funzione search_quantities precedente. Questa
# infatti restituisce i valori dei dizonari come stringa anche se questi sarebbero in
# realtà valori. Allora quello che fa è se sono convertibili li converte in float o int
# in base a cosa sarà necessario


def try_parse_number(value: str):
    # Prova a convertire una stringa in int o float. Se non riesce, restituisce None.
    try:
        if '.' in value:
            return float(value)
        else:
            return int(value)
    except (ValueError, TypeError):
        return None


# Funzione necessaria per scriveere un valore numerico che potrebbe o meno essere dato
# insieme alla propria unità di misura. Bisognerebbe estenderlo al caso anche di
# funzioni vettoriali che perciò hanno una direzione (presente in nexus).


def generate_numeric_values(numeric_value, unit, output, target_path):
    if unit is not None:
        set_nested(output, target_path, {'value': numeric_value, 'unit': unit})
    else:
        set_nested(output, target_path, numeric_value)


# The next two functions are needed to read the dictionar obtained by the previous
# function. The first one obtain the value corresponding to the path in argument, while
# the other set in the specidifc position passed by path a value.


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


class SectionHeader(BaseModel):
    path: str
    type_class: str
    is_repeatable: bool | Callable | None = None


class Matcher:
    def __init__(
        self,
        target_group: 'SectionHeader' = None,
        values_to_save: dict = None,
        is_repeatable=None,
    ):
        self.target_group = target_group
        self.values_to_save = values_to_save
        self._is_repeatable = target_group.is_repeatable

    def check_repeatable(self, data, logger):
        """Calcola se è ripetibile con i dati a disposizione"""
        if callable(self._is_repeatable):
            return bool(self._is_repeatable(data))
        return bool(self._is_repeatable)

    def set_group(self, where, index, counter=None):
        path_to_group = self.target_group.path
        if 'eventID' in path_to_group:
            path_to_group = path_to_group.replace('ID', f'_{index}')
        if counter is not None:
            path_to_group = path_to_group.replace('*', f'{counter}')
        grp = where.require_group(path_to_group)
        grp.attrs['NX_class'] = self.target_group.type_class
        return grp

    def populate_attributes(self, grp, field, unit, attributi, input_dict):
        if unit is not None:
            grp[field].attrs['units'] = unit
        elif attributi is not None:
            for attr in attributi:
                grp[field].attrs[attr] = get_nested(input_dict, attributi[attr])

    def populate_not_repeatable_group(self, grp, dati_input, logger):
        if self.values_to_save is None:
            return
        fields = self.values_to_save.get('fields', None)
        if fields is not None:
            for field, rules in fields.items():
                alias = rules.get('alias', None)
                unit = rules.get('unit', None)
                metodo = rules.get('get', None)
                attributi = rules.get('attributes', None)
                data = None
                # Prova a prendere il valore dall'alias
                if alias is not None:
                    value = get_nested(dati_input, alias)
                    if isinstance(value, str) and value != '':
                        numeric_value = try_parse_number(value)
                        if numeric_value is not None:
                            data = numeric_value
                        elif metodo is not None:
                            data = metodo(value)
                        else:
                            data = value
                    elif isinstance(value, int | float):
                        data = value
                    # elif isinstance(value, list | tuple):
                    #    value = np.array(value)

                # Se non trovato tramite alias, prova il metodo
                if data is None and metodo is not None:
                    data = metodo(dati_input)
                # Se abbiamo un valore valido, creiamo il dataset
                if data is not None:
                    try:
                        grp.create_dataset(field, data=data)
                    except Exception as e:
                        logger.info(f'Field {field} already compiled in {grp}.')
                        logger.warning(f'{e}')
                    self.populate_attributes(grp, field, unit, attributi, dati_input)

    def generate_repeatable_groups(self, where, index, dati_input, logger):
        logger.info(f'Il gruppo {where} è risultato ripetibile uso la routine giusta')
        src = self.values_to_save.get('src', None)
        fields = self.values_to_save.get('repeatable_fields')
        mix_dict = get_nested(dati_input, src) if src is not None else dati_input

        if mix_dict is None:
            return

        for field_name, pattern in fields.items():
            regex = re.compile(pattern)

            # iteratore ordinato delle chiavi che matchano
            matches_iter = sorted(k for k in mix_dict if regex.fullmatch(k))
            for idx, match in enumerate(matches_iter):
                grp = self.set_group(where, index, idx)
                value = get_nested(mix_dict, match)
                grp.create_dataset(field_name, data=value)


base_matchers = [
    Matcher(
        SectionHeader(
            path='./instrument/', type_class='NXem_instrument', is_repeatable=False
        ),
        {
            'fields': {
                'name': {'alias': 'Make'},
            }
        },
    ),
    Matcher(
        SectionHeader(
            path='./instrument/program', type_class='NXprogram', is_repeatable=False
        ),
        {
            'fields': {
                'name': {'alias': 'Software'},
            }
        },
    ),
    Matcher(
        SectionHeader(
            path='./measurement/eventID/',
            type_class='NXem_event_data',
            is_repeatable=False,
        ),
        {},
    ),
]
