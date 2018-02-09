#!/usr/bin/python3
from jinja2 import Environment, FileSystemLoader

def createffserverconf(keys):
    env = Environment(loader=FileSystemLoader('ffconf'))
    template = env.get_template('templateffserver.conf')
    output_from_parsed_template = template.render(range=keys)
    # to save the results
    with open("ffconf/ffserver.conf", "w") as fh:
        fh.write(output_from_parsed_template)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
