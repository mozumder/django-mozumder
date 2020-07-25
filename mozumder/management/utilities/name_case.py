import re

def verbose_to_CamelCase(str, separator=' '):
    return ''.join([re.sub('[^A-Za-z0-9]+', '', n).title() for n in str.split(separator)])

def verbose_to_snake_case(str, separator=' ', joiner='_'):
    return joiner.join([re.sub('[^A-Za-z0-9]+', '', n).lower() for n in str.split(separator)])

def CamelCase_to_snake_case(str, separator='_'):
    return separator.join(re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', str)).lower()

def CamelCase_to_verbose(str, separator=' '):
    return separator.join(re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', str)).title()

def snake_case_to_verbose(str):
    return ' '.join(str.split('_')).title()
