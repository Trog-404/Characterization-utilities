import re

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
