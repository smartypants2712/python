#!/usr/bin/python

from xml.etree import ElementTree as ET
from pom_utils import *
from pprint import pprint, pformat
from prettytable import PrettyTable
import sys
import re
import os
import logging

POM_FILENAME = 'pom.xml'
WORKING_DIR = os.getcwd()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def parse_project_pom():
    parent_pom_path = os.path.join(WORKING_DIR,POM_FILENAME)
    # parse project parent pom
    if os.path.isfile(POM_FILENAME):
        logger.info('Parsing project parent pom %s ...' % parent_pom_path)
        parent_pom_tree = ET.ElementTree()
        parent_pom_tree.parse(parent_pom_path)
    else:
        logger.error('%s does not exist in %s' % (parent_pom_path, WORKING_DIR))
        sys.exit(1)
    return parent_pom_tree

def gen_project_dep():
    parent_pom_tree = parse_project_pom()
    parent_pom_path = os.path.join(WORKING_DIR,POM_FILENAME)

    # build version map from project parent pom
    # this assumes that ALL the project dependency versions are defined here, in the parent pom,
    # and not in any of the child/module poms
    p_pom_version_map = build_version_map(parent_pom_tree)

    # get list of project modules
    modules = get_modules(parent_pom_tree)

    child_pom_paths = []
    if modules:
        for module in modules:
            child_pom_path = os.path.join(WORKING_DIR, module, POM_FILENAME)
            if not os.path.isfile(child_pom_path):
                logger.warning('WARNING: Module POM not found at %s' % child_pom_path)
            else:
                child_pom_paths.append(child_pom_path)
    child_pom_paths.append(parent_pom_path)  # sometimes dependencies are also specified in the project parent pom

    # aggregate all the dependencies from all the project pom files
    project_dep = {}
    build_dependency_list(child_pom_paths, input_type='file', dict=project_dep)

    logger.info('Resolving project pom dependency versions ...')
    resolve_versions(project_dep, p_pom_version_map)

    return [project_dep, p_pom_version_map]

def gen_master_pom_dep():
    parent_pom_tree = parse_project_pom()
    m_pom = get_master_pom_version(parent_pom_tree)  # Get master or base pom version from project pom
    if m_pom:
        logger.info('Using %s version: %s' % (m_pom['artifactId'], m_pom['version']))
    else:
        logger.error('Unable to retrieve master/base pom version from project pom')
        sys.exit(1)

    logger.info('Compiling list of dependency versions from master POM ...')
    url = ''
    if m_pom['artifactId'] == 'master-pom':
        url = get_latest_pom_url(GLOBAL_POM_PATH, m_pom['version'])
    elif m_pom['artifactId'] == 'base-pom':
        url = get_latest_pom_url(BASE_POM_PATH, m_pom['version'])
    else:
        logger.error('Unknown pom-type')
        return
    m_pom_version_map = build_version_map(url)  # need to work for both master-pom and base-pom

    # parse base-pom/master-pom, common-lib-pom, third-party-lib-pom to build list of dependencies
    logger.info('Compiling list of master/base POM dependencies ...')
    m_pom_dep = {}
    if m_pom['artifactId'] == 'master-pom':
        master_pom_url = get_latest_pom_url(MASTER_POM_PATH, m_pom['version'])
        third_party_pom_url = get_latest_pom_url(THIRD_PARTY_LIB_POM_PATH, m_pom['version'])
        common_pom_url = get_latest_pom_url(COMMON_LIB_POM_PATH, m_pom['version'])
        m_pom_dep = build_dependency_list([master_pom_url, third_party_pom_url, common_pom_url], input_type='url', dict=m_pom_dep)
    elif m_pom['artifactId'] == 'base-pom':
        base_pom_url = get_latest_pom_url(BASE_POM_PATH, m_pom['version'])
        m_pom_dep = build_dependency_list([base_pom_url], input_type='url', dict=m_pom_dep)
    else:
        logger.error('Unknown pom-type - should be master-pom or base-pom')
        sys.exit(1)

    logger.info('Resolving master pom dependency versions ...')
    resolve_versions(m_pom_dep, m_pom_version_map)

    return [m_pom_dep, m_pom_version_map]


def compare(project_dep, m_pom_dep):
    p_dep_keys = set([k for k in project_dep])
    m_dep_keys = set([k for k in m_pom_dep])
    common_keys = p_dep_keys & m_dep_keys

    to_be_removed = set()
    for k in common_keys:
        if not project_dep[k]:  # filter out blank/empty versions
            to_be_removed.add(k)
        if not m_pom_dep[k]:  # filter out blank/empty versions
            to_be_removed.add(k)
        if project_dep[k] >= m_pom_dep[k]:  # filter out versions that are the same or greater
            to_be_removed.add(k)
    common_keys.difference_update(to_be_removed)

    return common_keys


def main():
    logger.info('***** Processing project POMs *****')
    [project_dep, p_pom_version_map] = gen_project_dep()

    logger.info('***** Processing Master POM *****')
    [m_pom_dep, m_pom_version_map] = gen_master_pom_dep()

    logger.info('Using master pom version map to resolve project dependencies ...')
    resolve_versions(project_dep, m_pom_version_map)

    logger.debug('Dependencies and versions specified in project POM:')
    logger.debug(pformat(project_dep))

    logger.debug('Dependencies and versions specified in master POM:')
    logger.debug(pformat(m_pom_dep))

    logger.info('***** Version overrides in project component POM *****')
    common_keys = compare(project_dep, m_pom_dep)
    if common_keys:
        t = PrettyTable(["Dependency", "Master POM Version", "Project POM Version"])
        t.align["Dependency"] = "l"  # Left align dependencies column
        for k in common_keys:
            t.add_row([k, m_pom_dep[k], project_dep[k]])
        print t
    else:
        logger.info('No master POM dependencies were overwritten with a lower version in project POM')


if __name__ == "__main__":
    main()
