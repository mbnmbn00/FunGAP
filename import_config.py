'''Import config function'''

import os
import json


def import_config():
    '''Import config'''
    this_path = os.path.realpath(__file__)
    this_dir = os.path.dirname(this_path)
    config_file = os.path.join(this_dir, 'fungap_config.json')
    with open(config_file) as f_in:
        d_conf = json.load(f_in)
    return d_conf
