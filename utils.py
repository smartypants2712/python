#!/usr/bin/python

import urllib2
import json
import sys
import os
import glob
import datetime


class FixedHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    """
    Overrides the redirect_request method in urllib2 to support HTTP DELETE.
    For reasons unknown, the server always tries to redirect you and the original
    redirect_request does not support DELETE.
    """
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        m = req.get_method()
        if (code in (301, 302, 303, 307) and m in ("GET", "HEAD")
            or code in (301, 302, 303) and m in ("POST", "DELETE")):
            newurl = newurl.replace(' ', '%20')
            newheaders = dict((k,v) for k,v in req.headers.items()
                              if k.lower() not in ("content-length", "content-type")
                             )
            newrequest = urllib2.Request(newurl,
                                 headers=newheaders,
                                 origin_req_host=req.get_origin_req_host(),
                                 unverifiable=True)
            newrequest.get_method = req.get_method
            return newrequest
        else:
            raise urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)

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
    
def encode_utf8(input):
    if isinstance(input, dict):
        return {encode_utf8(k): encode_utf8(v) for k, v in input.iteritems()}
    elif isinstance(input, list):
        return [encode_utf8(x) for x in input]
    elif isinstance(input, unicode):
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
