#!/usr/bin/python

from xml.etree import ElementTree as ET
import urllib2
import re
import logging

ARTIFACTORY_REPO_URL = 'http://www.dummy.com:8080/repo/'
ARTIFACTORY_API_URL = 'http://www.dummy.com:8080/api/'
GLOBAL_POM_PATH = 'com/sso/maven/global-pom'
MASTER_POM_PATH = 'com/sso/maven/master-pom'
COMMON_LIB_POM_PATH = 'com/sso/maven/common-lib-pom'
THIRD_PARTY_LIB_POM_PATH = 'com/sso/maven/third-party-lib-pom'
BASE_POM_PATH = 'com/sso/pom/base-pom'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_latest_pom_url(path, version=''):
    if not version:
        url = ARTIFACTORY_REPO_URL + path + '/' + 'maven-metadata.xml'
        logger.debug('Getting latest pom version from %s ' % url)
        request = urllib2.Request(url)
        metadata = ET.fromstring(urllib2.urlopen(request).read())
        version = metadata.findall('versioning/latest')
        if not version:
            logger.error('Unable to get latest version. Please check!!')
            return None
        else:
            version = version[0].text
    #print 'Getting pom version : %s' % version
    
    url2 = ARTIFACTORY_REPO_URL + path + '/' + version + '/' + 'maven-metadata.xml'
    logger.debug('Getting latest pom version from %s ' % url2)
    request2 = urllib2.Request(url2)
    metadata2 = ET.fromstring(urllib2.urlopen(request2).read())
    artifactId = metadata2.find('artifactId').text
    if not artifactId:
        logger.error('Error retrieving artifactId from maven metadata')
        return None
    snapshot_version = metadata2.find('versioning/snapshotVersions/snapshotVersion/value').text
    if not snapshot_version:
        logger.error('Error retrieving snapshotVersion from maven metadata')
        return None
    
    return ARTIFACTORY_REPO_URL + path + '/' + version + '/' + artifactId + '-' + snapshot_version + '.pom'

def get_master_pom_version(etree):
    ns = get_namespace(etree)
    aid_elem = etree.find(ns+'parent/'+ns+'artifactId')
    if len(aid_elem):
        logger.error('Parent element not found!')
        return
    version_elem = etree.find(ns+'parent/'+ns+'version')
    if len(version_elem):
        logger.error('Parent/version element not found!')
        return
    if aid_elem.text == 'master-pom':
        logger.info('Using master-pom')
    elif aid_elem.text == 'base-pom':
        logger.warning('!!BASE-POM WARNING!! Project is still using base-pom, which should be phased-out. Please use master-pom instead.')
    else:
        logger.error('Unknown parent/artifactId: %s' % aid_elem.text)
        return

    return {'artifactId': aid_elem.text, 'version': version_elem.text}


def get_namespace(etree):
    namespace = ''
    root_tag = etree.getroot().tag
    if root_tag.lower() != 'project':
        match = re.search('\{(.*)\}',root_tag)
        namespace = match.group(0)
        logger.debug('POM file has a namespace: %s' % namespace)
    else:
        logger.debug('POM file has no namespace')
    return namespace
    
def get_modules(etree):
    namespace = get_namespace(etree)
    modules_tree = etree.findall(namespace + 'modules/' + namespace + 'module')
    if modules_tree:
        modules = [ module.text for module in modules_tree ]
        logger.info('Modules found in project POM: ' + str(modules))
        return modules
    else:
        logger.info('No modules found in project POM')
        return None


def to_element_tree(input):
    if type(input) == type(ET.ElementTree()):
        return input
    logger.debug('Path to pom file: %s' % input)
    tree = ET.ElementTree()
    try:
        request = urllib2.Request(input)
        tree.parse(urllib2.urlopen(request))
        return tree
    except (IOError, OSError):
        pass
    try:
        tree.parse(input)
        return tree
    except (IOError, OSError):
        pass
    return None

# Build the version map from global-pom, or any other pomfile (${artifact.version} -> 1.2.3)
def build_version_map(input, version_map=None):
    if not version_map: version_map = {}
    tree = to_element_tree(input)
    if tree is None:
        logger.error('ERROR: Unknown input type - input must be a URL, path to a file, or an ElementTree')
        return version_map
    ns = get_namespace(tree)
    properties = tree.find(ns + 'properties')
    if len(properties):
        for p in properties:
            property_key = re.sub('\{.*\}','',p.tag)
            property_val = p.text
            logger.debug(property_key + ' - ' + property_val)
            if property_key in version_map:
                logger.debug('Skipping %s ... already exists' % property_key)
            else:
                version_map[property_key] = property_val
    return version_map

# Resolve/replace the version variables in a dependency list with values in version_map (replace ${artifact.version} with 1.2.3)
def resolve_versions(dict, version_map):
    if not dict:
        logger.error('Input must be a non-empty dictionary')
    for key in dict:
        version_str = re.sub('[\${}]','',dict[key])
        if version_str in version_map:
            dict[key] = version_map.get(version_str)
    return dict

# Build the list of dependencies (mavan path -> artifact version) with any pom file
def build_dependency_list(inputs, input_type='url', dict=None):
    for input in inputs:
        logger.info('Parsing %s ...' % input)
        tree = ET.ElementTree()
        if input_type == 'url':
            request = urllib2.Request(input)
            tree.parse(urllib2.urlopen(request))
        elif input_type == 'file':
            tree.parse(input)
        else:
            logger.error('ERROR: Unknown input type')
            return dict

        ns = get_namespace(tree)
        dependencies = tree.findall(ns + 'dependencyManagement/' + ns + 'dependencies/' + ns + 'dependency') + tree.findall(ns + 'dependencies/' + ns + 'dependency')
        if len(dependencies):
            for d in dependencies:
                gid = d.find(ns + 'groupId').text
                aid = d.find(ns + 'artifactId').text
                version_elem = d.find(ns + 'version')
                version = ''
                if version_elem is not None:
                    version = version_elem.text
                if re.search('pom',aid): continue # if the artifactId is a pom file, we don't care (only care about libraries)
                mvn_path = gid + '.' + aid
                logger.debug('artifactId and version: %s, %s' % (mvn_path, version))
                if mvn_path in dict:
                    #print 'Dependency ' + mvn_path + ' already exists in the list of project dependencies with value: ' + dict[mvn_path] + '; the new value: ' + version + ' will not be added.'
                    logger.debug('Skipping %s ... already exists' % mvn_path)
                else:
                    dict[mvn_path] = version
                #ex = d.findall('exclusions/exclusion')
                #if ex:
                #    for e in ex:
                #        e_gid = e.find('groupId').text
                #        e_aid = e.find('artifactId').text
                #        print '\t Exclusion: ' + e_gid + '.' + e_aid
        else:
            logger.warning('WARNING: No dependencies found in POM file!')
    
    return dict

def main():
    version_map = {} # artifact -> version
    dep_dict = {}

    version = '2.8.0-SNAPSHOT'
    version_map = parse_global_pom(version)

    # parse master-pom, common-lib-pom, third-party-lib-pom to build list of dependencies
    dep_dict = build_dependency_list(version)

    dep_dict = resolve_versions(dep_dict, version_map)

    for key, val in dep_dict.items():
        logger.info('%s: %s' % (key, val))

    
if __name__ == "__main__":
    main()


