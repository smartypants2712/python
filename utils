#!/usr/bin/python

import urllib2, json
import sys, os, glob
import datetime

def get_json(url, headers=''):
    request = urllib2.Request(url)
    for key in headers:
        request.add_header(key, headers[key])
        try:
            response = json.load(urllib2.urlopen(request))
            return response
        except urllib2.URLError as e:
            print 'URLError:', e
            print 'URL:', url
        except urllib2.HTTPError as e:
            print 'HTTPError:', e
            print 'URL:', url
        except ValueError as e:
            print 'ValueError:', e
            print 'URL:', url

def load_json(full_path):
    try:
        f = open(full_path)
        response = json.load(f)
    except IOError, e:
        print 'I/O Error: Could not open file!'
        print e
    return response
    
def to_UTF8(input):
    if isinstance(input,dict):
        return {to_UTF8(k):to_UTF8(v) for k,v in input.iteritems()}
    elif isinstance(input,list):
        return [to_UTF8(x) for x in input]
    elif isinstance(input,unicode):
        return input.encode('utf-8')
    else:
        return input

def write_to_file(json_input, filename):
    if filename=='':
        print 'Error: Missing filename'
        return
    current_dir = os.getcwd()
    if os.path.exists(ARCHIVE_DIR):
        os.chdir(ARCHIVE_DIR)
    else:
        print 'Error: Could not find archive directory',ARCHIVE_DIR
        return
    f = open(filename,'wb')
    print 'Writing to file',filename,'...'
    json.dump(json_input,f)
    print 'Write complete.'    
    os.chdir(current_dir)

def load_archive(env_name):
    print 'Loading from archive ...'
    components = []
    archive_list = find_files(env_name)
    if archive_list:
        try:
            latest_file = max(archive_list)
            full_path = ARCHIVE_DIR + '/' + latest_file
            print 'Loading',full_path
            f = open(full_path)
            components = json.load(f)
        except Exception, e:
            print 'Error loading archive file!'
            print e
    else:
        print 'Error: no archive files found!'
    return components

def find_files(env_name):
    current_dir = os.getcwd()
    if os.path.exists(ARCHIVE_DIR):
        os.chdir(ARCHIVE_DIR)
    else:
        print 'Error: Could not find archive directory',ARCHIVE_DIR
        return
    if env_name=='':
        print 'Error: Missing environment name'
        return
    search_str = 'env_info-'+env_name+'_*.json'
    results = glob.glob(search_str)
    os.chdir(current_dir)
    return results
