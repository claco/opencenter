#!/usr/bin/env python

import json
import logging
import os
import sys


LOG = logging.getLogger(__name__)


backend_list = {}


class Backend(object):
    def __init__(self, path):
        self.facts = []
        self.primitives = []

        my_path = os.path.dirname(path)
        json_path = os.path.join(my_path, 'primitives.json')
        fact_path = os.path.join(my_path, 'facts.json')

        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                self.primitives = json.loads(f.read())

        if os.path.exists(fact_path):
            with open(fact_path, 'r') as f:
                self.facts = json.loads(f.read())


def load():
    for file_name in os.listdir(os.path.dirname(__file__)):
        full_path = os.path.join(os.path.dirname(__file__), file_name)
        if os.path.isdir(full_path):
            init_path = os.path.join(full_path, '__init__.py')
            if os.path.exists(full_path):
                print 'trying to load %s' % full_path
                import_str = 'roush.backends.%s' % file_name
                class_str = '%sBackend' % ''.join(map(lambda x: x.capitalize(),
                                                      file_name.split('-')))
                try:
                    __import__(import_str)
                    backend_list[file_name] = getattr(sys.modules[import_str],
                                                      class_str)()
                except Exception as e:
                    print('Cannot load %s from %s: %s' % (
                            class_str, import_str, str(e)))
