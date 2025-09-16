import re

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
    name: str | None
    type_class: str


class Matcher:
    def __init__(
        self, target_group: 'SectionHeader' = None, values_to_save: dict = None
    ):
        self.target_group = target_group
        self.values_to_save = values_to_save

    def set_group(self, where):
        grp = where.require_group(self.target_group.path)
        grp.attrs['NX_class'] = self.target_group.type_class
        return grp

    def populate_group(self, grp, dati_input):
        if self.values_to_save is not None:
            for field, rules in self.values_to_save.items():
                alias = rules.get('alias', None)
                unit = rules.get('unit', None)
                metodo = rules.get('get', None)
                # Prima prova con l'alias
                value_found = False
                if alias is not None:
                    value = get_nested(dati_input, alias)
                    if isinstance(value, str) and value != '':
                        numeric_value = try_parse_number(value)
                        if numeric_value is not None:
                            grp.create_dataset(field, data=numeric_value)
                            if unit is not None:
                                grp[field].attrs['units'] = unit
                            break
                        if metodo is not None:
                            new = metodo(value)
                            grp.create_dataset(field, data=new)
                            break
                        else:
                            # non parsabile -> salvo come stringa
                            grp.create_dataset(field, data=value)
                            break
                    elif isinstance(value, int | float):
                        grp.create_dataset(field, data=value)
                        break
                    value_found = True
                    break
                # Se non è stato trovato nessun valore in alias prova con il metodo get
                if not value_found and metodo is not None:
                    computed_value = metodo(dati_input)
                    if computed_value is not None:
                        grp.create_dataset(field, data=computed_value)
