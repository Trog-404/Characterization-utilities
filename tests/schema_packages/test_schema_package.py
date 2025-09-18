import os.path

from nomad.client import normalize_all, parse


def test_schema_package():
    test_file = os.path.join('tests', 'data', 'test.archive.yaml')
    entry = parse(test_file)[0]
    normalize_all(entry)
    prova = entry.data.name
    assert prova is not None
