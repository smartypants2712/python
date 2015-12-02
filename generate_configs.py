#!/bin/python

import os
import re
import sys
import glob
from xml.etree import ElementTree as ET
from optparse import OptionParser

CONFIGKEY_XPATH = './/ConfigKey'
TOKEN_PATTERN = r'{__(.+?)__}'
CHECKMARK = 'OK' #u'\u2713'
CROSSMARK = 'FAILED' #u'\u2717'
CONFIG_OUTPUT_DIR = 'config_output'
CONFIG_TEMPLATE_DIR = 'config_templates'
LOOKUP_FILENAME = 'config_lookup.xml'


class ConfigXML:
    def __init__(self, path):
        self.fullpath = os.path.abspath(path)
        self.dir = self.fullpath.split(os.sep)[:-1]
        self.filename = self.fullpath.split(os.sep)[-1]
        self.tree = ET.ElementTree()
        self.tree.parse(path)
        self.dict = self.create_dict()

    def create_dict(self):
        d = {}
        elem_list = self.tree.findall(CONFIGKEY_XPATH)
        for elem in elem_list:
            key = elem.attrib['Name']
            value = elem.attrib['Value']
            d[key] = value
        return d

    def set_config_value(self, key, value):
        elem = self.tree.find('.//ConfigKey[@Name="' + key + '"]')
        elem.attrib['Value'] = value

    def write(self, output_path):
        print 'Writing file: %s ... ' % output_path,
        self.tree.write(output_path, encoding="utf-8", xml_declaration=True)
        print CHECKMARK


class ConfigLookup:
    def __init__(self, lookup_file):
        if os.path.isdir(lookup_file):
            lookup_file = os.path.join(lookup_file, LOOKUP_FILENAME)
        self.filepath = os.path.abspath(lookup_file)
        self.tree = ET.parse(lookup_file)

    def get(self, component, app, prop=''):
        if prop:
            xpath = './/' + component + '/' + app + '_' + prop
        else:
            xpath = './/' + component + '/' + app
        return self.tree.find(xpath).text


def generate_config(config_template, app, config_lookup):
    t = ConfigXML(config_template)
    for k in t.dict:
        results = re.findall(TOKEN_PATTERN, t.dict[k])
        if results:
            template_value = t.dict[k]
            for r in results:
                prop = ''
                after_split = r.split('_')
                if len(after_split) == 2:
                    component, prop = after_split
                elif len(after_split) == 1:
                    component = after_split[0]
                else:
                    print 'ERROR reading token %s in configuration template. Too many values after string split' % r
                    raise Exception()
                if prop:
                    value = config_lookup.get(component.lower(), app, prop.lower())
                else:
                    value = config_lookup.get(component.lower(), app)
                token = '{__' + r + '__}'
                template_value = template_value.replace(token, value)
            actual_value = template_value
            t.set_config_value(k, actual_value)
        else:
            continue
    if not os.path.exists(CONFIG_OUTPUT_DIR):
        os.mkdir(CONFIG_OUTPUT_DIR)
    output_path = os.path.join(CONFIG_OUTPUT_DIR, app.upper())
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    output_filename = t.filename.replace('template.xml', app.upper() + '.xml')
    output = os.path.join(output_path, output_filename)
    t.write(output)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-l', dest='lookup_file', help='Path to config_lookup.xml', default=CONFIG_TEMPLATE_DIR)
    parser.add_option('-t', dest='template_file', help='Path to config template file(s)', default=CONFIG_TEMPLATE_DIR)
    parser.add_option('-a', action="store_true", dest='app1', default=False, help='Generate file for APP1')
    parser.add_option('-b', action="store_true", dest='app2', default=False, help='Generate file for APP2')
    parser.add_option('-v', action="store_true", dest='verbose', default=False, help='Verbose mode')
    (options, args) = parser.parse_args()

    if not options.app1 and not options.app2:
        print 'Not generating files for APP1 or APP2. Nothing to do. Bye!'
        sys.exit(0)
    cl = ConfigLookup(options.lookup_file)
    if os.path.isfile(options.template_file):
        template_list = [options.template_file]
    elif os.path.isdir(options.template_file):
        template_list = sorted(glob.glob(os.path.join(options.template_file, '*_configuration_template.xml')))
    else:
        print ('ERROR: Invalid template file path. Path is neither a file nor a directory.')
        raise Exception()
    for template in template_list:
        if options.app1:
            print 'Generating configuration XML for APP1 ...'
            generate_config(template, 'app1', cl)
        if options.app2:
            print 'Generating configuration XML for APP2 ...'
            generate_config(template, 'app2', cl)

