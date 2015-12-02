#!/bin/python

import os
import re
import glob
from xml.etree import ElementTree as ET
from optparse import OptionParser

CONFIGKEY_XPATH = './/ConfigKey'
CHECKMARK = 'OK' #u'\u2713'
CROSSMARK = 'FAILED' #u'\u2717'
URL_PATTERN = re.compile(r'https:\/\/(.+?)(-app2\.mycompany\.com|\.mycompany\.com):?([0-9]{4})?')
HOST_PATTERN = re.compile(r'https://(.+?)(?=:|/)')
PORT_PATTERN = re.compile(r'https://.+?:([0-9]+)')
LOOKUP_FILENAME = 'config_lookup.xml'
CONFIG_TEMPLATE_DIR = 'config_templates'
SPECIAL_COMPONENTS = ['special.component']

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


class CompareConfigXML:
    def __init__(self, a, b):
        self.a_diff_b = list(set(a.dict.keys()) - set(b.dict.keys()))
        self.b_diff_a = list(set(b.dict.keys()) - set(a.dict.keys()))
        self.intersection = list(set(a.dict.keys()).intersection(set(b.dict.keys())))
        self.unmatched_value_keys = []
        for k in self.intersection:
            if a.dict[k] != b.dict[k]:
                self.unmatched_value_keys.append(k)


def generate_lookup(config_a, config_b, unmatched_value_keys):
    print 'Generating config lookup file ... ',
    rel_path = os.path.join(CONFIG_TEMPLATE_DIR, LOOKUP_FILENAME)
    if not os.path.exists(rel_path):
        config_keys_tag = ET.Element('ConfigKeys')
        tree = ET.ElementTree(config_keys_tag)
    else:
        tree = ET.parse(rel_path)
    root = tree.getroot()
    existing_keys = [e.tag for e in root]

    for k in unmatched_value_keys:
        result_a = URL_PATTERN.match(config_a.dict[k])
        result_b = URL_PATTERN.match(config_b.dict[k])
        is_url = True
        if result_a:
            if len(result_a.groups()) > 2:
                port_a = result_a.groups()[2]
            component_a = result_a.groups()[0].replace('-app2', '')
        if result_b:
            if len(result_b.groups()) > 2:
                port_b = result_b.groups()[2]
            component_b = result_b.groups()[0].replace('-app2', '')
        if not result_a and not result_b:
            is_url = False
        if not is_url:
            component = k
            component_a = config_a.dict[k]
            component_b = config_b.dict[k]
        elif component_a == component_b or component_a in SPECIAL_COMPONENTS:
            component = component_a
        else:
            print 'Something is wrong. Hostnames in APP1 and APP2 are too different - %s and %s' % (component_a, component_b)
            raise Exception()
        if component not in existing_keys:
            if is_url:
                if component in SPECIAL_COMPONENTS:
                    app1_host = component_a + '.mycompany.com'
                    app2_host = component_b + '.mycompany.com'
                else:
                    app1_host = component + '.mycompany.com'
                    app2_host = component + '-app2.mycompany.com'
                app1_port = port_a if port_a else ''
                app2_port = port_b if port_b else ''
                component_elem = ET.SubElement(root, component.lower())
                app1_host_elem = ET.SubElement(component_elem, 'app1_host')
                app1_host_elem.text = app1_host
                app2_host_elem = ET.SubElement(component_elem, 'app2_host')
                app2_host_elem.text = app2_host
                app1_port_elem = ET.SubElement(component_elem, 'app1_port')
                app1_port_elem.text = app1_port
                app2_port_elem = ET.SubElement(component_elem, 'app2_port')
                app2_port_elem.text = app2_port
                existing_keys.append(component)
            else:
                component_elem = ET.SubElement(root, component.lower())
                app1_elem = ET.SubElement(component_elem, 'app1')
                app1_elem.text = component_a
                app2_elem = ET.SubElement(component_elem, 'app2')
                app2_elem.text = component_b
                existing_keys.append(component)
    print CHECKMARK
    print 'Writing file: %s ... ' % os.path.abspath(rel_path),
    tree.write(rel_path, encoding="utf-8", xml_declaration=True)
    print CHECKMARK


def generate_template(config_a, unmatched_value_keys):
    print 'Generating templatized config file ... ',
    elem_list = config_a.tree.findall(CONFIGKEY_XPATH)
    for elem in elem_list:
        if elem.attrib['Name'] in unmatched_value_keys:
            value_str = elem.attrib['Value']
            result = URL_PATTERN.match(value_str)
            if result:
                component = result.groups()[0].replace('-app2', '')
                host_token = '{__' + component.upper() + '_HOST__}'
                port_token = '{__' + component.upper() + '_PORT__}'
                host_match = HOST_PATTERN.match(value_str)
                port_match = PORT_PATTERN.match(value_str)
                if host_match:
                    value_str = value_str.replace(host_match.groups()[0], host_token)
                if port_match:
                    value_str = value_str.replace(port_match.groups()[0], port_token)
            else:
                value_str = '{__' + elem.attrib['Name'].upper() + '__}'
            elem.attrib['Value'] = value_str
    print CHECKMARK
    a.write(os.path.join(os.getcwd(), CONFIG_TEMPLATE_DIR, config_a.filename.replace('.xml', '_template.xml')))

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-a', dest='path_a', help='Path to file A OR directory of files')
    parser.add_option('-b', dest='path_b', help='Path to file B OR directory of files')
    parser.add_option('-v', action="store_true", dest='verbose', default=False, help='Verbose mode')
    (options, args) = parser.parse_args()

    if not os.path.exists(CONFIG_TEMPLATE_DIR):
        os.mkdir(CONFIG_TEMPLATE_DIR)
    if (os.path.isfile(options.path_a) != os.path.isfile(options.path_b)) or \
       (os.path.isdir(options.path_a) != os.path.isdir(options.path_b)):
        print 'ERROR: Type mismatch - you must specify either two files or two directories. \
        Or one of the files or directories could not be found.'
        raise Exception()
    filelist_a = []
    filelist_b = []
    if os.path.isfile(options.path_a) and os.path.isfile(options.path_b):
        filelist_a.append(os.path.abspath(options.path_a))
        filelist_b.append(os.path.abspath(options.path_b))
    elif os.path.isdir(options.path_a) and os.path.isdir(options.path_b):
        dir_a = os.path.abspath(options.path_a)
        dir_b = os.path.abspath(options.path_b)
        filelist_a = sorted(glob.glob(os.path.join(dir_a, '*_configuration.xml')))
        filelist_b = sorted(glob.glob(os.path.join(dir_b, '*_configuration.xml')))
    else:
        print 'ERROR: Type mismatch - you must specify either two files or two directories. \
        Or one of the files or directories could not be found.'
        raise Exception()
    if len(filelist_a) != len(filelist_b):
        print 'ERROR: Number of files in A and B are different!'
        raise Exception()
    for file_a, file_b in zip(filelist_a, filelist_b):
        if not os.path.exists(file_a):
            print 'ERROR: File not found - %s' % file_a
            raise Exception()
        if not os.path.exists(file_b):
            print 'ERROR: File not found - %s' % file_b
            raise Exception()
        print '== Processing %s and %s ... ' % (file_a, file_b)
        a = ConfigXML(file_a)
        b = ConfigXML(file_b)
        cc = CompareConfigXML(a, b)
        if options.verbose:
            if cc.a_diff_b:
                print '== Keys in A but not in B =='
                for key in cc.a_diff_b:
                    print key + ': ' + a.dict[key]
            if cc.b_diff_a:
                print '== Keys in B but not in A =='
                for key in cc.b_diff_a:
                    print key + ': ' + b.dict[key]
            print '== Same keys but different values =='
            for k in cc.unmatched_value_keys:
                print 'A: ' + k + ' = ' + a.dict[k]
                print 'B: ' + k + ' = ' + b.dict[k]
        print 'File A and B have the identical keys ... ',
        if not cc.a_diff_b and not cc.b_diff_a:
            print CHECKMARK
            if cc.unmatched_value_keys:
                generate_lookup(a, b, cc.unmatched_value_keys)
                generate_template(a, cc.unmatched_value_keys)
            else:
                print 'All the keys and values are the same between %s and %s. Nothing to do here.' % (file_a, file_b)
        else:
            print CROSSMARK
            print 'Make sure the two input files have identical keys before running this script again'
