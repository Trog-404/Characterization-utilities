from characterization_utilities.convert.em_convert.utils import (
    Matcher,
    SectionHeader,
)

matchers = [
    Matcher(
        SectionHeader(path='./instrument/', type_class='NXem_instrument'),
        {'name': {'alias': 'Make'}},
    ),
    Matcher(
        SectionHeader(path='./instrument/program', type_class='NXprogram'),
        {'program': {'alias': 'Software'}},
    ),
]
